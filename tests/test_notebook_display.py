from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pandas as pd
import plotly.graph_objects as go
import polars as pl
import pytest

from faircareai.notebook import (
    DisplayError,
    NotebookDisplay,
    detect_notebook_platform,
    normalize_display_options,
)


def test_detection_prefers_databricks_then_fabric_then_marimo_then_jupyter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABRICKS_RUNTIME_VERSION", "15.4")
    monkeypatch.setitem(sys.modules, "notebookutils", ModuleType("notebookutils"))
    assert detect_notebook_platform(get_ipython=lambda: object()) == "databricks"

    monkeypatch.delenv("DATABRICKS_RUNTIME_VERSION")
    assert detect_notebook_platform(get_ipython=lambda: object()) == "fabric"

    monkeypatch.delitem(sys.modules, "notebookutils")
    monkeypatch.setitem(sys.modules, "marimo", ModuleType("marimo"))
    assert detect_notebook_platform(get_ipython=lambda: object()) == "jupyter"
    assert detect_notebook_platform(get_ipython=lambda: None) == "marimo"

    monkeypatch.delitem(sys.modules, "marimo")
    assert detect_notebook_platform(get_ipython=lambda: object()) == "jupyter"
    assert detect_notebook_platform(get_ipython=lambda: None) == "terminal"


def test_normalizes_sections_and_options_before_display() -> None:
    options = normalize_display_options(
        sections="all", platform="jupyter", max_rows=1000, plotlyjs="cdn"
    )
    assert options.sections == (
        "summary",
        "overall",
        "subgroups",
        "disparities",
        "calibration",
        "flags",
        "figures",
    )

    assert normalize_display_options(
        sections=["flags", "summary", "flags"],
        platform="auto",
        max_rows=1,
        plotlyjs="inline",
    ).sections == ("flags", "summary")

    with pytest.raises(ValueError, match="Unknown.*mystery"):
        normalize_display_options(sections=["summary", "mystery"])
    with pytest.raises(ValueError, match="between 1 and 10,000"):
        normalize_display_options(max_rows=10_001)
    with pytest.raises(ValueError, match="platform"):
        normalize_display_options(platform="spark")  # type: ignore[arg-type]
    assert normalize_display_options(platform="marimo").platform == "marimo"
    with pytest.raises(ValueError, match="plotlyjs"):
        normalize_display_options(plotlyjs="yes")  # type: ignore[arg-type]


def test_injected_display_functions_receive_pandas_and_plotly_html() -> None:
    tables_seen: list[pd.DataFrame] = []
    html_seen: list[str] = []
    text_seen: list[str] = []
    display = NotebookDisplay(
        platform="jupyter",
        display_table=tables_seen.append,
        display_html=html_seen.append,
        display_text=text_seen.append,
    )

    display.render(
        summary="Audit complete",
        tables={"overall": pl.DataFrame({"metric": ["auroc"], "value": [0.8]})},
        figures={"calibration": go.Figure(go.Scatter(x=[0, 1], y=[0, 1]))},
        sections=["summary", "overall", "figures"],
        max_rows=100,
        plotlyjs="cdn",
    )

    assert text_seen == ["Audit complete"]
    assert len(tables_seen) == 1
    assert list(tables_seen[0].columns) == ["metric", "value"]
    assert len(html_seen) == 1
    assert "plotly" in html_seen[0].lower()
    assert "cdn.plot.ly" in html_seen[0]


def test_table_rows_are_bounded_and_unknown_section_fails_before_output() -> None:
    tables_seen: list[pd.DataFrame] = []
    display = NotebookDisplay(platform="jupyter", display_table=tables_seen.append)
    table = pl.DataFrame({"row": range(10)})

    display.render(tables={"overall": table}, sections="overall", max_rows=3)
    assert len(tables_seen[0]) == 3

    with pytest.raises(ValueError, match="Unknown"):
        display.render(tables={"overall": table}, sections=["overall", "bad"])
    assert len(tables_seen) == 1


def test_figure_failure_is_actionable_and_retains_section() -> None:
    def fail_html(_html: str) -> None:
        raise RuntimeError("blocked")

    display = NotebookDisplay(platform="fabric", display_html=fail_html)

    with pytest.raises(DisplayError, match=r"figures.*save_artifacts.*html"):
        display.render(
            figures={"subgroup": go.Figure()}, sections="figures", plotlyjs="inline"
        )


def test_terminal_fallback_prints_summary_and_tables(capsys: pytest.CaptureFixture[str]) -> None:
    display = NotebookDisplay(platform="terminal")
    display.render(
        summary="Audit complete",
        tables={"overall": pl.DataFrame({"metric": ["auroc"], "value": [0.8]})},
        figures={"calibration": go.Figure()},
        sections=["summary", "overall", "figures"],
    )

    output = capsys.readouterr().out
    assert "Audit complete" in output
    assert "auroc" in output
    assert "interactive figures require a notebook" in output.lower()


def test_marimo_display_uses_native_output_apis(monkeypatch: pytest.MonkeyPatch) -> None:
    output: list[object] = []
    fake_marimo = SimpleNamespace(
        output=SimpleNamespace(append=output.append),
        ui=SimpleNamespace(table=lambda value, **kwargs: ("table", value, kwargs)),
        Html=lambda value: ("html", value),
        md=lambda value: ("markdown", value),
    )
    monkeypatch.setitem(sys.modules, "marimo", fake_marimo)
    display = NotebookDisplay(platform="marimo")

    display.render(
        summary="Audit complete",
        tables={"overall": pl.DataFrame({"metric": ["auroc"], "value": [0.8]})},
        figures={"calibration": go.Figure(go.Scatter(x=[0, 1], y=[0, 1]))},
        sections=["summary", "overall", "figures"],
    )

    assert output[0] == ("markdown", "```text\nAudit complete\n```")
    assert output[1][0] == "table"
    assert output[1][2] == {"selection": None}
    assert output[2][0] == "html"


def test_marimo_display_gives_install_guidance_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(sys.modules, "marimo", raising=False)
    real_import_module = __import__("importlib").import_module

    def fail_marimo_import(name: str, *args: object, **kwargs: object) -> ModuleType:
        if name == "marimo":
            raise ImportError("marimo is not installed")
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr("faircareai.notebook.importlib.import_module", fail_marimo_import)
    with pytest.raises(DisplayError, match=r"pip install marimo"):
        NotebookDisplay(platform="marimo")
