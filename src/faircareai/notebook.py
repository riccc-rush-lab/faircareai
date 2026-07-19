"""Runtime-neutral notebook display helpers for FairCareAI results."""

from __future__ import annotations

import importlib
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd
import polars as pl

from faircareai.core.exceptions import FairCareAIError

NotebookPlatform = Literal["auto", "fabric", "databricks", "jupyter"]
ResolvedPlatform = Literal["fabric", "databricks", "jupyter", "terminal"]
PlotlyJsMode = Literal["cdn", "inline"]

SECTION_ORDER = (
    "summary",
    "overall",
    "subgroups",
    "disparities",
    "calibration",
    "flags",
    "figures",
)
_PUBLIC_PLATFORMS = {"auto", "fabric", "databricks", "jupyter"}
_RESOLVED_PLATFORMS = {"fabric", "databricks", "jupyter", "terminal"}


class DisplayError(FairCareAIError):
    """Raised when a validated results section cannot be displayed."""


@dataclass(frozen=True)
class DisplayOptions:
    """Validated notebook presentation options."""

    sections: tuple[str, ...]
    platform: NotebookPlatform
    max_rows: int
    plotlyjs: PlotlyJsMode


def normalize_display_options(
    sections: str | Sequence[str] = "all",
    *,
    platform: NotebookPlatform = "auto",
    max_rows: int = 1_000,
    plotlyjs: PlotlyJsMode = "cdn",
) -> DisplayOptions:
    """Validate display arguments before any notebook output is emitted."""

    normalized_sections = _normalize_sections(sections)
    if platform not in _PUBLIC_PLATFORMS:
        raise ValueError(
            "platform must be one of: auto, fabric, databricks, jupyter"
        )
    if isinstance(max_rows, bool) or not isinstance(max_rows, int) or not 1 <= max_rows <= 10_000:
        raise ValueError("max_rows must be an integer between 1 and 10,000")
    if plotlyjs not in {"cdn", "inline"}:
        raise ValueError("plotlyjs must be either 'cdn' or 'inline'")
    return DisplayOptions(normalized_sections, platform, max_rows, plotlyjs)


def detect_notebook_platform(
    *, get_ipython: Callable[[], Any] | None = None
) -> ResolvedPlatform:
    """Detect Databricks, then Fabric, then Jupyter without eager dependencies."""

    if any(
        os.environ.get(name)
        for name in ("DATABRICKS_RUNTIME_VERSION", "DB_IS_DRIVER", "DATABRICKS_HOST")
    ):
        return "databricks"

    try:
        importlib.import_module("notebookutils")
    except ImportError:
        pass
    else:
        return "fabric"

    ipython_getter = get_ipython
    if ipython_getter is None:
        try:
            import IPython
        except ImportError:
            ipython_getter = None
        else:
            ipython_getter = IPython.get_ipython
    if ipython_getter is not None:
        try:
            if ipython_getter() is not None:
                return "jupyter"
        except Exception:
            pass
    return "terminal"


class NotebookDisplay:
    """Render result components with native or injected notebook functions."""

    def __init__(
        self,
        *,
        platform: ResolvedPlatform,
        display_table: Callable[[pd.DataFrame], Any] | None = None,
        display_html: Callable[[str], Any] | None = None,
        display_text: Callable[[str], Any] | None = None,
    ) -> None:
        if platform not in _RESOLVED_PLATFORMS:
            raise ValueError(f"Unsupported resolved notebook platform: {platform}")
        defaults = _default_display_functions(platform)
        self.platform = platform
        self._display_table = display_table or defaults[0]
        self._display_html = display_html or defaults[1]
        self._display_text = display_text or defaults[2]

    def render(
        self,
        *,
        summary: str | None = None,
        tables: Mapping[str, pl.DataFrame | pd.DataFrame] | None = None,
        figures: Mapping[str, Any] | None = None,
        sections: str | Sequence[str] = "all",
        max_rows: int = 1_000,
        plotlyjs: PlotlyJsMode = "cdn",
    ) -> None:
        """Render validated sections, truncating tables to the notebook limit."""

        options = normalize_display_options(
            sections, platform="jupyter", max_rows=max_rows, plotlyjs=plotlyjs
        )
        available_tables = tables or {}
        available_figures = figures or {}

        for section in options.sections:
            if section == "summary":
                if summary is not None:
                    self._render_text(summary, section)
                continue
            if section == "figures":
                self._render_figures(available_figures, options.plotlyjs)
                continue
            table = available_tables.get(section)
            if table is not None:
                self._render_table(table, section, options.max_rows)

    def _render_text(self, value: str, section: str) -> None:
        try:
            self._display_text(value)
        except Exception as exc:
            raise DisplayError(f"Could not display {section} section: {exc}") from exc

    def _render_table(
        self, table: pl.DataFrame | pd.DataFrame, section: str, max_rows: int
    ) -> None:
        if isinstance(table, pl.DataFrame):
            pandas_table = table.head(max_rows).to_pandas()
        elif isinstance(table, pd.DataFrame):
            pandas_table = table.head(max_rows)
        else:
            raise TypeError(f"Table section '{section}' must be a Polars or pandas DataFrame")
        try:
            self._display_table(pandas_table)
        except Exception as exc:
            raise DisplayError(f"Could not display {section} table: {exc}") from exc

    def _render_figures(self, figures: Mapping[str, Any], plotlyjs: PlotlyJsMode) -> None:
        if self.platform == "terminal":
            if figures:
                self._display_text(
                    "Interactive figures require a notebook; export them explicitly or call "
                    "save_artifacts(..., formats=('html',))."
                )
            return

        for name, figure in figures.items():
            try:
                html = figure.to_html(full_html=False, include_plotlyjs=plotlyjs)
                self._display_html(html)
            except Exception as exc:
                raise DisplayError(
                    f"Could not display figures section ({name}). Use "
                    "save_artifacts(..., formats=('html',)) instead: "
                    f"{exc}"
                ) from exc


def create_notebook_display(
    platform: NotebookPlatform = "auto",
    *,
    display_table: Callable[[pd.DataFrame], Any] | None = None,
    display_html: Callable[[str], Any] | None = None,
    display_text: Callable[[str], Any] | None = None,
) -> NotebookDisplay:
    """Create a display adapter for an explicit or auto-detected platform."""

    options = normalize_display_options(platform=platform)
    resolved: ResolvedPlatform
    if options.platform == "auto":
        resolved = detect_notebook_platform()
    else:
        resolved = options.platform
    return NotebookDisplay(
        platform=resolved,
        display_table=display_table,
        display_html=display_html,
        display_text=display_text,
    )


def _normalize_sections(sections: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(sections, str):
        requested = [sections]
    else:
        requested = list(sections)
    if not requested:
        raise ValueError("At least one display section is required")
    if "all" in requested:
        if requested != ["all"]:
            raise ValueError("'all' cannot be combined with individual display sections")
        return SECTION_ORDER

    unknown = [name for name in requested if name not in SECTION_ORDER]
    if unknown:
        raise ValueError(
            f"Unknown display section(s): {', '.join(map(str, unknown))}. "
            f"Supported sections: {', '.join(SECTION_ORDER)}"
        )
    return tuple(dict.fromkeys(requested))


def _default_display_functions(
    platform: ResolvedPlatform,
) -> tuple[Callable[[pd.DataFrame], Any], Callable[[str], Any], Callable[[str], Any]]:
    if platform in {"fabric", "databricks"}:
        import builtins

        table_display = getattr(builtins, "display", None)
        html_display = getattr(builtins, "displayHTML", None)
        if callable(table_display) and callable(html_display):
            return table_display, html_display, print

    if platform == "jupyter":
        try:
            from IPython.display import HTML, display

            return display, lambda value: display(HTML(value)), display
        except ImportError:
            pass

    return print, print, print
