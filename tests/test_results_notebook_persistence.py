"""Focused tests for notebook presentation and managed-platform persistence."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from faircareai.core.config import FairnessConfig
from faircareai.core.results import AuditResults


@pytest.fixture
def results() -> AuditResults:
    return AuditResults(
        config=FairnessConfig(model_name="Readmission", model_version="3.0"),
        audit_id="audit-123",
        run_timestamp="2026-07-18T12:00:00Z",
        overall_performance={
            "discrimination": {"auroc": 0.82, "auroc_ci_95": [0.79, 0.85]},
            "calibration": {"calibration_slope": 0.94},
        },
        subgroup_performance={
            "race": {
                "groups": {
                    "A": {
                        "n": 80,
                        "auroc": 0.81,
                        "auroc_ci_95": [0.76, 0.86],
                        "oe_ratio": 1.07,
                        "suppressed_in_reports": False,
                    },
                    "B": {
                        "n": 8,
                        "auroc": 0.70,
                        "suppressed_in_reports": True,
                    },
                },
                "disparities": {"B": {"auroc_difference": -0.11}},
            }
        },
        fairness_metrics={"race": {"tpr_diff": {"A": 0.0, "B": -0.08}, "suppressed_groups": ["B"]}},
        flags=[
            {
                "metric": "tpr_diff",
                "attribute": "race",
                "group": "B",
                "value": -0.08,
                "status": "warn",
            }
        ],
    )


def test_to_tables_returns_presentation_ready_polars_frames(results: AuditResults) -> None:
    tables = results.to_tables()

    assert set(tables) == {"overall", "subgroups", "disparities", "calibration", "flags"}
    assert all(isinstance(table, pl.DataFrame) for table in tables.values())
    assert tables["subgroups"].filter(pl.col("group") == "A")["n"].item() == 80
    assert set(tables["calibration"]["metric"]) == {"calibration_slope", "oe_ratio"}
    hidden = tables["subgroups"].filter(pl.col("group") == "B")
    assert hidden["value"].item() is None
    assert hidden["display_value"].item() == "suppressed (n<11)"


def test_to_metrics_frame_has_stable_schema_and_aggregate_only_rows(
    results: AuditResults,
) -> None:
    frame = results.to_metrics_frame()

    assert frame.columns == [
        "audit_id",
        "run_timestamp",
        "model_name",
        "model_version",
        "section",
        "attribute",
        "group",
        "metric",
        "value",
        "ci_lower",
        "ci_upper",
        "n",
        "status",
        "suppressed_in_reports",
    ]
    auroc = frame.filter(
        (pl.col("section") == "subgroup") & (pl.col("group") == "A") & (pl.col("metric") == "auroc")
    ).row(0, named=True)
    assert auroc["value"] == pytest.approx(0.81)
    assert auroc["ci_lower"] == pytest.approx(0.76)
    assert auroc["ci_upper"] == pytest.approx(0.86)
    assert auroc["n"] == 80
    suppressed = frame.filter((pl.col("group") == "B") & (pl.col("section") == "subgroup"))
    assert suppressed["suppressed_in_reports"].to_list() == [True]
    disparity = frame.filter((pl.col("group") == "B") & (pl.col("metric") == "auroc_difference"))
    assert disparity.height == 1
    assert disparity["suppressed_in_reports"].item() is True


def test_show_delegates_validated_tables_and_figures(results: AuditResults) -> None:
    display = MagicMock()
    figure = MagicMock()
    with (
        patch("faircareai.notebook.create_notebook_display", return_value=display) as factory,
        patch.object(results, "plot_discrimination", return_value=figure),
        patch.object(results, "plot_overall_calibration", return_value=figure),
        patch.object(results, "plot_decision_curve", return_value=figure),
        patch.object(results, "plot_subgroup_performance", return_value=figure),
        patch.object(results, "plot_subgroup_calibration", return_value=figure),
    ):
        returned = results.show(platform="fabric", max_rows=25)

    assert returned is results
    factory.assert_called_once_with("fabric")
    kwargs = display.render.call_args.kwargs
    assert kwargs["sections"] == "all"
    assert kwargs["max_rows"] == 25
    assert set(kwargs["figures"]) == {
        "discrimination",
        "overall_calibration",
        "decision_curve",
        "subgroup_comparison",
        "subgroup_calibration_race",
    }


def test_plot_subgroup_calibration_uses_requested_attribute(results: AuditResults) -> None:
    figure = MagicMock()
    with patch(
        "faircareai.visualization.subgroup_plots.create_subgroup_calibration_pair_plot",
        return_value=figure,
    ) as plot:
        returned = results.plot_subgroup_calibration("race")

    assert returned is figure
    plot.assert_called_once_with(
        results.subgroup_performance["race"], title="Subgroup Calibration by race"
    )

    with pytest.raises(ValueError, match="unknown"):
        results.plot_subgroup_calibration("unknown")


def test_save_artifacts_stages_into_audit_directory_and_guards_overwrite(
    results: AuditResults, tmp_path: Path
) -> None:
    with patch.object(
        results, "to_html", side_effect=lambda path, **_: Path(path).write_text("html")
    ):
        paths = results.save_artifacts(tmp_path, formats=("html", "json"))

    assert paths == {
        "html": tmp_path / "audit-123" / "report.html",
        "json": tmp_path / "audit-123" / "metrics.json",
    }
    assert paths["html"].read_text() == "html"
    assert '"audit_id": "audit-123"' in paths["json"].read_text()

    with pytest.raises(FileExistsError, match="overwrite=True"):
        results.save_artifacts(tmp_path, formats=("json",))

    paths = results.save_artifacts(tmp_path, formats=("json",), overwrite=True)
    assert paths["json"].exists()


def test_save_artifacts_supports_all_documented_formats(
    results: AuditResults, tmp_path: Path
) -> None:
    def write(path: str | Path, **_: object) -> Path:
        target = Path(path)
        target.write_bytes(b"artifact")
        return target

    with (
        patch.object(results, "to_html", side_effect=write),
        patch.object(results, "to_json", side_effect=write),
        patch.object(results, "to_png", side_effect=write),
        patch.object(results, "to_pdf", side_effect=write),
        patch.object(results, "to_pptx", side_effect=write),
    ):
        paths = results.save_artifacts(tmp_path, formats=("html", "json", "png", "pdf", "pptx"))

    assert set(paths) == {"html", "json", "png", "pdf", "pptx"}
    assert all(path.exists() for path in paths.values())


class _FakeWriter:
    def __init__(self) -> None:
        self.format_name: str | None = None
        self.mode_name: str | None = None
        self.table: str | None = None

    def format(self, value: str) -> "_FakeWriter":
        self.format_name = value
        return self

    def mode(self, value: str) -> "_FakeWriter":
        self.mode_name = value
        return self

    def saveAsTable(self, value: str) -> None:  # noqa: N802
        self.table = value


class _FakeSparkFrame:
    def __init__(self) -> None:
        self.write = _FakeWriter()


class _FakeExistingTable:
    def __init__(self, count: int) -> None:
        self._count = count
        self.filter_expression: str | None = None

    def where(self, expression: str) -> "_FakeExistingTable":
        self.filter_expression = expression
        return self

    def limit(self, _value: int) -> "_FakeExistingTable":
        return self

    def count(self) -> int:
        return self._count


class _FakeCatalog:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    def tableExists(self, _table: str) -> bool:  # noqa: N802
        return self._exists


class _FakeSpark:
    def __init__(self, *, exists: bool = False, duplicate_count: int = 0) -> None:
        self.catalog = _FakeCatalog(exists)
        self.existing = _FakeExistingTable(duplicate_count)
        self.created = _FakeSparkFrame()
        self.created_input = None

    def table(self, _table: str) -> _FakeExistingTable:
        return self.existing

    def createDataFrame(self, value: object) -> _FakeSparkFrame:  # noqa: N802
        self.created_input = value
        return self.created


def test_save_delta_appends_normalized_metrics(results: AuditResults) -> None:
    spark = _FakeSpark()

    returned = results.save_delta(spark, "catalog.schema.audit_metrics")

    assert returned == "catalog.schema.audit_metrics"
    assert spark.created.write.format_name == "delta"
    assert spark.created.write.mode_name == "append"
    assert spark.created.write.table == "catalog.schema.audit_metrics"
    assert list(spark.created_input.columns) == results.to_metrics_frame().columns


def test_save_delta_rejects_duplicate_audit_id_and_existing_error_table(
    results: AuditResults,
) -> None:
    duplicate_spark = _FakeSpark(exists=True, duplicate_count=1)
    with pytest.raises(ValueError, match="audit-123"):
        results.save_delta(duplicate_spark, "audit_metrics")

    existing_spark = _FakeSpark(exists=True)
    with pytest.raises(FileExistsError, match="audit_metrics"):
        results.save_delta(existing_spark, "audit_metrics", mode="error")
