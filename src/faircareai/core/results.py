"""
FairCareAI Audit Results Container

Container for fairness audit results with export and visualization capabilities.

Metrics computed per Van Calster et al. (2025) methodology. Healthcare
organizations interpret results based on their clinical context,
organizational values, and governance frameworks.
"""

import json
import os
import shutil
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

import numpy as np
import polars as pl

if TYPE_CHECKING:
    import plotly.graph_objects as go

    from faircareai.reports.generator import AuditSummary
    from faircareai.reports.pptx_options import PptxOptions

from faircareai.core.config import FairnessConfig, MetricDisplayConfig, OutputPersona
from faircareai.core.logging import get_logger
from faircareai.visualization.themes import GOVERNANCE_DISCLAIMER_SHORT

logger = get_logger(__name__)


@dataclass
class AuditResults:
    """Container for fairness audit results with export capabilities.

    This is the main output from FairCareAudit.run(). It contains all
    computed metrics, flags, and provides methods for visualization
    and report generation.

    Attributes:
        config: FairnessConfig used for the audit.
        descriptive_stats: Section 1 - Table 1 cohort summary.
        overall_performance: Section 2 - TRIPOD+AI metrics.
        subgroup_performance: Section 3 - Performance by sensitive attribute.
        fairness_metrics: Section 4 - Fairness metrics per attribute.
        intersectional: Intersectional analysis results.
        flags: List of metrics outside configured thresholds.
        governance_recommendation: Section 7 - Summary statistics.
    """

    config: FairnessConfig
    threshold: float = 0.5  # Decision threshold used for classification metrics

    # Audit metadata
    audit_id: str = field(default_factory=lambda: str(uuid4()))
    run_timestamp: str | None = None
    random_seed: int | None = None
    reproducibility: dict = field(default_factory=dict)

    # Results - IN ORDER OF REPORT SECTIONS
    # Section 1: Descriptive Statistics (Table 1)
    descriptive_stats: dict = field(default_factory=dict)

    # Section 2: Overall Model Performance
    overall_performance: dict = field(default_factory=dict)

    # Section 3: Subgroup Performance
    subgroup_performance: dict = field(default_factory=dict)

    # Section 4: Fairness Metrics
    fairness_metrics: dict = field(default_factory=dict)
    intersectional: dict = field(default_factory=dict)

    # Section 5: Flags & Warnings
    flags: list[dict] = field(default_factory=list)

    # Section 7: Governance Advisory
    governance_recommendation: dict = field(default_factory=dict)

    # Internal reference to audit for raw data access
    _audit: Any = None

    def summary(self) -> str:
        """Print summary to console.

        Returns:
            Formatted summary string.
        """
        desc = self.descriptive_stats
        cohort = desc.get("cohort_overview", {})
        perf = self.overall_performance
        disc = perf.get("discrimination", {})
        cal = perf.get("calibration", {})
        cls = perf.get("classification_at_threshold", {})
        gov = self.governance_recommendation

        # Format metrics safely - handles None and numeric values
        def fmt(val: Any, fmt_str: str = ".3f") -> str:
            if val is None:
                return "N/A"
            try:
                return f"{val:{fmt_str}}"
            except (TypeError, ValueError):
                return "N/A"

        # Safe percentage formatting - handles 0.0 correctly (0.0 is falsy but valid)
        def fmt_pct(val: Any) -> str:
            if val is None:
                return "N/A"
            return f"{val * 100:.1f}"

        # Cache repeated dict access for efficiency
        n_total = cohort.get("n_total")
        n_positive = cohort.get("n_positive")
        prevalence_pct = cohort.get("prevalence_pct", "N/A")

        # Format N values
        n_total_str = f"{n_total:,}" if isinstance(n_total, int | float) else str(n_total or "N/A")
        n_positive_str = (
            f"{n_positive:,}" if isinstance(n_positive, int | float) else str(n_positive or "N/A")
        )

        # Get Brier score from calibration dict (correct location)
        brier_score = cal.get("brier_score")

        # Get classification metrics safely
        sensitivity = cls.get("sensitivity")
        specificity = cls.get("specificity")
        ppv = cls.get("ppv")
        pct_flagged = cls.get("pct_flagged")

        lines = [
            "=" * 70,
            "FairCareAI Fairness Analysis Results",
            "=" * 70,
            f"Model: {self.config.model_name} v{self.config.model_version}",
            "",
            "SECTION 1: COHORT SUMMARY",
            f"  N:              {n_total_str}",
            f"  Outcome:        {n_positive_str} ({prevalence_pct})",
            "",
            "SECTION 2: OVERALL MODEL PERFORMANCE (TRIPOD+AI)",
            "  Discrimination:",
            f"    AUROC:        {fmt(disc.get('auroc'))} {disc.get('auroc_ci_fmt', '')}",
            f"    AUPRC:        {fmt(disc.get('auprc'))} {disc.get('auprc_ci_fmt', '')}",
            "  Calibration:",
            f"    Brier Score:  {fmt(brier_score, '.4f')}",
            f"    Cal. Slope:   {fmt(cal.get('calibration_slope'), '.2f')} (ideal: 1.00)",
            f"  At Threshold = {cls.get('threshold', 'N/A')}:",
            f"    Sensitivity:  {fmt_pct(sensitivity)}%",
            f"    Specificity:  {fmt_pct(specificity)}%",
            f"    PPV:          {fmt_pct(ppv)}%",
            f"    % Flagged:    {fmt(pct_flagged, '.1f') if pct_flagged is not None else 'N/A'}%",
            "",
            "SECTION 4: FAIRNESS SUMMARY",
            f"  Primary metric: {self.config.primary_fairness_metric.value if self.config.primary_fairness_metric else 'Not set'}",
            "",
            "SECTION 7: RESULTS SUMMARY",
            f"  Within threshold: {gov.get('n_pass', gov.get('within_threshold_count', 0))}",
            f"  Near threshold: {gov.get('n_warnings', gov.get('near_threshold_count', 0))}",
            f"  Outside threshold: {gov.get('n_errors', gov.get('outside_threshold_count', 0))}",
            "",
            "=" * 70,
            f"  {GOVERNANCE_DISCLAIMER_SHORT}",
            "=" * 70,
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self.summary()

    # === Table 1 Methods ===

    def print_table1(self) -> str:
        """Print Table 1 descriptive statistics.

        Returns:
            Formatted Table 1 string.
        """
        from faircareai.metrics.descriptive import format_table1_text

        text = format_table1_text(self.descriptive_stats)
        logger.info("Table 1:\n%s", text)
        return text

    def get_table1_dataframe(self) -> pl.DataFrame:
        """Get Table 1 as a Polars DataFrame for export.

        Returns:
            Polars DataFrame with Table 1 data.
        """
        from faircareai.metrics.descriptive import generate_table1_dataframe

        return generate_table1_dataframe(self.descriptive_stats)

    # === Visualization Methods ===

    def plot_discrimination(self) -> "go.Figure":
        """Plot ROC and Precision-Recall curves (TRIPOD+AI 2.1).

        Returns:
            Plotly Figure with side-by-side curves.
        """
        from faircareai.visualization.performance_charts import plot_discrimination_curves

        return plot_discrimination_curves(self)

    def plot_overall_calibration(self) -> "go.Figure":
        """Plot calibration curve for overall model (TRIPOD+AI 2.2).

        Returns:
            Plotly Figure with calibration curve.
        """
        from faircareai.visualization.performance_charts import plot_calibration_curve

        return plot_calibration_curve(self)

    def plot_threshold_analysis(self, selected_threshold: float | None = None) -> "go.Figure":
        """Interactive threshold sensitivity analysis (TRIPOD+AI 2.4).

        Data scientist can TOGGLE threshold to see metric impacts.

        Args:
            selected_threshold: Threshold to highlight (default: primary threshold).

        Returns:
            Plotly Figure with threshold analysis.
        """
        from faircareai.visualization.performance_charts import plot_threshold_analysis

        thresh = selected_threshold or self.overall_performance.get("primary_threshold", 0.5)
        return plot_threshold_analysis(self, selected_threshold=thresh)

    def plot_decision_curve(self) -> "go.Figure":
        """Plot Decision Curve Analysis for clinical utility (TRIPOD+AI 2.5).

        Returns:
            Plotly Figure with DCA curves.
        """
        from faircareai.visualization.performance_charts import plot_decision_curve

        return plot_decision_curve(self)

    def plot_calibration(self, by: str | None = None) -> "go.Figure":
        """Plot calibration curve(s).

        Args:
            by: Sensitive attribute to stratify by (None for overall).

        Returns:
            Plotly Figure with calibration curve(s).
        """
        from faircareai.visualization.plots import create_calibration_plot

        if by is None:
            return self.plot_overall_calibration()

        if self._audit is None:
            raise ValueError("Stratified calibration requires AuditResults._audit to be set.")

        df = self._audit.df
        y_true = np.asarray(df[self._audit.y_true_col].to_numpy())
        y_prob = np.asarray(df[self._audit.y_prob_col].to_numpy())
        group_labels = np.asarray(df[by].to_numpy())

        return create_calibration_plot(
            y_true=y_true,
            y_prob=y_prob,
            group_labels=group_labels,
            title=f"Calibration by {by}",
        )

    def plot_fairness_dashboard(self) -> "go.Figure":
        """Plot comprehensive fairness dashboard.

        Returns:
            Plotly Figure with 4-panel fairness dashboard.
        """
        from faircareai.visualization.governance_dashboard import (
            create_fairness_dashboard,
        )

        return create_fairness_dashboard(self)

    def plot_subgroup_performance(self, metric: str = "auroc") -> "go.Figure":
        """Plot subgroup performance comparison.

        Args:
            metric: Metric to compare ('auroc', 'tpr', 'fpr', 'ppv').

        Returns:
            Plotly Figure with subgroup comparison.
        """
        from faircareai.visualization.governance_dashboard import (
            plot_subgroup_comparison,
        )

        return plot_subgroup_comparison(self, metric=metric)

    def plot_subgroup_calibration(self, attribute: str) -> "go.Figure":
        """Plot observed:expected ratio and calibration slope by subgroup."""
        from faircareai.visualization.subgroup_plots import (
            create_subgroup_calibration_pair_plot,
        )

        if attribute not in self.subgroup_performance:
            available = ", ".join(map(str, self.subgroup_performance)) or "none"
            raise ValueError(
                f"Unknown sensitive attribute '{attribute}'. Available attributes: {available}"
            )
        return create_subgroup_calibration_pair_plot(
            self.subgroup_performance[attribute],
            title=f"Subgroup Calibration by {attribute}",
        )

    def plot_executive_summary(self) -> "go.Figure":
        """Plot executive summary for governance committee.

        Single-page visual with:
        - Traffic light status
        - Key metrics at a glance
        - Worst disparity highlighted
        - Plain language interpretation

        Returns:
            Plotly Figure with executive summary.
        """
        from faircareai.visualization.governance_dashboard import (
            create_executive_summary,
        )

        return create_executive_summary(self)

    def plot_go_nogo_scorecard(self) -> "go.Figure":
        """Plot scorecard for governance presentation.

        Returns:
            Plotly Figure with checklist-style scorecard.
        """
        from faircareai.visualization.governance_dashboard import (
            create_go_nogo_scorecard,
        )

        return create_go_nogo_scorecard(self)

    # === Notebook and persistence methods ===

    def to_metrics_frame(self) -> pl.DataFrame:
        """Return normalized, aggregate-only metrics with a stable schema."""
        rows: list[dict[str, Any]] = []

        for category, metrics in self.overall_performance.items():
            if not isinstance(metrics, dict):
                continue
            section = "calibration" if category == "calibration" else "overall"
            rows.extend(self._metric_rows(section=section, metrics=metrics))

        for attribute, attribute_data in self.subgroup_performance.items():
            if not isinstance(attribute_data, dict):
                continue
            groups = attribute_data.get("groups", {})
            if isinstance(groups, dict):
                for group, group_data in groups.items():
                    if not isinstance(group_data, dict):
                        continue
                    n = _as_int(group_data.get("n"))
                    suppressed = bool(group_data.get("suppressed_in_reports", False))
                    for metric, value in group_data.items():
                        section = (
                            "calibration"
                            if metric in {"oe_ratio", "calibration_slope"}
                            else "subgroup"
                        )
                        row = self._metric_row(
                            section=section,
                            metric=metric,
                            value=value,
                            metrics=group_data,
                            attribute=str(attribute),
                            group=str(group),
                            n=n,
                            suppressed=suppressed,
                        )
                        if row is not None:
                            rows.append(row)

            disparities = attribute_data.get("disparities", {})
            if isinstance(disparities, dict):
                for group, group_metrics in disparities.items():
                    if not isinstance(group_metrics, dict):
                        continue
                    group_data = groups.get(group, {}) if isinstance(groups, dict) else {}
                    is_suppressed = isinstance(group_data, dict) and bool(
                        group_data.get("suppressed_in_reports", False)
                    )
                    rows.extend(
                        self._metric_rows(
                            section="disparity",
                            metrics=group_metrics,
                            attribute=str(attribute),
                            group=str(group),
                            suppressed_groups={str(group)} if is_suppressed else set(),
                        )
                    )

        for attribute, metrics in self.fairness_metrics.items():
            if isinstance(metrics, dict):
                suppressed_groups = {str(group) for group in metrics.get("suppressed_groups", [])}
                rows.extend(
                    self._metric_rows(
                        section="disparity",
                        metrics=metrics,
                        attribute=str(attribute),
                        suppressed_groups=suppressed_groups,
                    )
                )

        for flag in self.flags:
            rows.append(
                self._base_metric_row(
                    section="flag",
                    attribute=_as_string(flag.get("attribute")),
                    group=_as_string(flag.get("group")),
                    metric=str(flag.get("metric", "flag")),
                    value=_as_float(flag.get("value")),
                    n=_as_int(flag.get("n")),
                    status=_as_string(flag.get("status") or flag.get("severity")),
                    suppressed=bool(flag.get("suppressed_in_reports", False)),
                )
            )

        schema = {
            "audit_id": pl.String,
            "run_timestamp": pl.String,
            "model_name": pl.String,
            "model_version": pl.String,
            "section": pl.String,
            "attribute": pl.String,
            "group": pl.String,
            "metric": pl.String,
            "value": pl.Float64,
            "ci_lower": pl.Float64,
            "ci_upper": pl.Float64,
            "n": pl.Int64,
            "status": pl.String,
            "suppressed_in_reports": pl.Boolean,
        }
        return pl.DataFrame(rows, schema=schema) if rows else pl.DataFrame(schema=schema)

    def to_tables(self) -> dict[str, pl.DataFrame]:
        """Return small presentation-ready tables used by notebook displays."""
        frame = self.to_metrics_frame()
        suppression_label = f"suppressed (n<{self.config.get_threshold('suppress_cell_n', 11)})"
        frame = frame.with_columns(
            pl.when(pl.col("suppressed_in_reports"))
            .then(pl.lit(suppression_label))
            .otherwise(pl.col("value").cast(pl.String))
            .alias("display_value"),
            pl.when(pl.col("suppressed_in_reports"))
            .then(None)
            .otherwise(pl.col("value"))
            .alias("value"),
            pl.when(pl.col("suppressed_in_reports"))
            .then(None)
            .otherwise(pl.col("ci_lower"))
            .alias("ci_lower"),
            pl.when(pl.col("suppressed_in_reports"))
            .then(None)
            .otherwise(pl.col("ci_upper"))
            .alias("ci_upper"),
        )
        return {
            "overall": frame.filter(pl.col("section") == "overall"),
            "subgroups": frame.filter(pl.col("section") == "subgroup"),
            "disparities": frame.filter(pl.col("section") == "disparity"),
            "calibration": frame.filter(pl.col("section") == "calibration"),
            "flags": frame.filter(pl.col("section") == "flag"),
        }

    def show(
        self,
        sections: str | Sequence[str] = "all",
        *,
        persona: OutputPersona | str = OutputPersona.DATA_SCIENTIST,
        platform: Literal["auto", "fabric", "databricks", "jupyter", "marimo"] = "auto",
        max_rows: int = 1_000,
        plotlyjs: Literal["cdn", "inline"] = "cdn",
    ) -> "AuditResults":
        """Render tables and Plotly figures in Fabric, Databricks, Jupyter, or marimo."""
        from faircareai.notebook import (
            create_notebook_display,
            normalize_display_options,
        )

        normalized_persona = _normalize_persona(persona)
        options = normalize_display_options(
            sections, platform=platform, max_rows=max_rows, plotlyjs=plotlyjs
        )
        display = create_notebook_display(platform)
        figures: dict[str, Any] = {}
        if "figures" in options.sections and display.platform != "terminal":
            if normalized_persona == OutputPersona.GOVERNANCE:
                figures = {
                    "executive_summary": self.plot_executive_summary(),
                    "go_nogo_scorecard": self.plot_go_nogo_scorecard(),
                }
            else:
                figures = {
                    "discrimination": self.plot_discrimination(),
                    "overall_calibration": self.plot_overall_calibration(),
                    "decision_curve": self.plot_decision_curve(),
                    "subgroup_comparison": self.plot_subgroup_performance(),
                }
                if self.subgroup_performance:
                    first_attribute = next(iter(self.subgroup_performance))
                    figures[f"subgroup_calibration_{first_attribute}"] = (
                        self.plot_subgroup_calibration(first_attribute)
                    )

        table_sections = {"overall", "subgroups", "disparities", "calibration", "flags"}
        tables = self.to_tables() if table_sections.intersection(options.sections) else {}
        display.render(
            summary=self.summary(),
            tables=tables,
            figures=figures,
            sections=sections,
            max_rows=max_rows,
            plotlyjs=plotlyjs,
        )
        return self

    def save_artifacts(
        self,
        destination: str | Path,
        *,
        formats: Sequence[Literal["html", "json", "png", "pdf", "pptx"]] = ("html", "json"),
        persona: OutputPersona | str = OutputPersona.DATA_SCIENTIST,
        overwrite: bool = False,
    ) -> dict[str, Path]:
        """Atomically stage HTML/JSON artifacts and copy them to an audit folder."""
        requested = tuple(dict.fromkeys(formats))
        if not requested:
            raise ValueError("At least one artifact format is required")
        filenames = {
            "html": "report.html",
            "json": "metrics.json",
            "png": "figures.zip",
            "pdf": "report.pdf",
            "pptx": "report.pptx",
        }
        unsupported = [name for name in requested if name not in filenames]
        if unsupported:
            raise ValueError(f"Unsupported artifact format(s): {', '.join(unsupported)}")
        normalized_persona = _normalize_persona(persona)

        output_dir = Path(destination) / self.audit_id
        final_paths: dict[str, Path] = {
            name: output_dir / filenames[name] for name in requested
        }
        existing = [path for path in final_paths.values() if path.exists()]
        if existing and not overwrite:
            raise FileExistsError(
                f"Artifact already exists: {existing[0]}. Pass overwrite=True to replace it."
            )

        with tempfile.TemporaryDirectory(prefix="faircareai-") as stage_dir:
            stage = Path(stage_dir)
            for artifact_format in requested:
                staged_path = stage / filenames[artifact_format]
                if artifact_format == "html":
                    self.to_html(staged_path, persona=normalized_persona)
                elif artifact_format == "json":
                    self.to_json(staged_path)
                elif artifact_format == "png":
                    self.to_png(staged_path, persona=normalized_persona)
                elif artifact_format == "pdf":
                    self.to_pdf(staged_path, persona=normalized_persona)
                elif artifact_format == "pptx":
                    self.to_pptx(staged_path, persona=normalized_persona)

            output_dir.mkdir(parents=True, exist_ok=True)
            temporary_paths: dict[str, Path] = {}
            try:
                for final_format, final_path in final_paths.items():
                    if not overwrite and final_path.exists():
                        raise FileExistsError(
                            f"Artifact already exists: {final_path}. Pass overwrite=True to replace it."
                        )
                    temporary = final_path.with_name(f".{final_path.name}.tmp")
                    shutil.copyfile(stage / filenames[final_format], temporary)
                    temporary_paths[final_format] = temporary
                for final_format, final_path in final_paths.items():
                    os.replace(temporary_paths[final_format], final_path)
            except Exception:
                for temporary in temporary_paths.values():
                    temporary.unlink(missing_ok=True)
                raise
        return final_paths

    def save_delta(
        self,
        spark: Any,
        table: str,
        *,
        mode: Literal["append", "error"] = "append",
    ) -> str:
        """Persist normalized metrics to a caller-selected Spark Delta table."""
        if mode not in {"append", "error"}:
            raise ValueError("mode must be either 'append' or 'error'")
        if not isinstance(table, str) or not table.strip():
            raise ValueError("table must be a non-empty string")

        exists = bool(spark.catalog.tableExists(table))
        if mode == "error" and exists:
            raise FileExistsError(f"Delta table already exists: {table}")
        if mode == "append" and exists:
            escaped_id = self.audit_id.replace("'", "''")
            duplicate_count = (
                spark.table(table)
                .where(f"audit_id = '{escaped_id}'")
                .limit(1)
                .count()
            )
            if duplicate_count:
                raise ValueError(
                    f"Audit {self.audit_id} is already present in Delta table {table}"
                )

        metrics_pdf = self.to_metrics_frame().to_pandas()
        try:
            from pyspark.sql.types import (
                BooleanType,
                DoubleType,
                LongType,
                StringType,
                StructField,
                StructType,
            )

            schema = StructType(
                [
                    StructField("audit_id", StringType(), True),
                    StructField("run_timestamp", StringType(), True),
                    StructField("model_name", StringType(), True),
                    StructField("model_version", StringType(), True),
                    StructField("section", StringType(), True),
                    StructField("attribute", StringType(), True),
                    StructField("group", StringType(), True),
                    StructField("metric", StringType(), True),
                    StructField("value", DoubleType(), True),
                    StructField("ci_lower", DoubleType(), True),
                    StructField("ci_upper", DoubleType(), True),
                    StructField("n", LongType(), True),
                    StructField("status", StringType(), True),
                    StructField("suppressed_in_reports", BooleanType(), False),
                ]
            )
            spark_frame = spark.createDataFrame(metrics_pdf, schema=schema)
        except ImportError:
            spark_frame = spark.createDataFrame(metrics_pdf)
        write_mode = "append" if mode == "append" else "errorifexists"
        spark_frame.write.format("delta").mode(write_mode).saveAsTable(table)
        return table

    def _metric_rows(
        self,
        *,
        section: str,
        metrics: dict[str, Any],
        attribute: str | None = None,
        group: str | None = None,
        suppressed_groups: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for metric, value in metrics.items():
            if isinstance(value, dict):
                for nested_group, nested_value in value.items():
                    row = self._metric_row(
                        section=section,
                        metric=metric,
                        value=nested_value,
                        metrics=value,
                        attribute=attribute,
                        group=str(nested_group),
                        suppressed=str(nested_group) in (suppressed_groups or set()),
                    )
                    if row is not None:
                        rows.append(row)
            else:
                row = self._metric_row(
                    section=section,
                    metric=metric,
                    value=value,
                    metrics=metrics,
                    attribute=attribute,
                    group=group,
                    suppressed=group in (suppressed_groups or set()) if group else False,
                )
                if row is not None:
                    rows.append(row)
        return rows

    def _metric_row(
        self,
        *,
        section: str,
        metric: str,
        value: Any,
        metrics: dict[str, Any],
        attribute: str | None = None,
        group: str | None = None,
        n: int | None = None,
        suppressed: bool = False,
    ) -> dict[str, Any] | None:
        if metric in {"n", "suppressed_in_reports"} or _is_metadata_metric(metric):
            return None
        numeric_value = _as_float(value)
        if numeric_value is None:
            return None
        ci = metrics.get(f"{metric}_ci_95", metrics.get(f"{metric}_ci"))
        ci_lower, ci_upper = _ci_bounds(ci)
        row = self._base_metric_row(
            section=section,
            attribute=attribute,
            group=group,
            metric=metric,
            value=numeric_value,
            n=n,
            suppressed=suppressed,
        )
        row["ci_lower"] = ci_lower
        row["ci_upper"] = ci_upper
        return row

    def _base_metric_row(
        self,
        *,
        section: str,
        attribute: str | None,
        group: str | None,
        metric: str,
        value: float | None,
        n: int | None,
        status: str | None = None,
        suppressed: bool = False,
    ) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "run_timestamp": self.run_timestamp,
            "model_name": self.config.model_name,
            "model_version": self.config.model_version,
            "section": section,
            "attribute": attribute,
            "group": group,
            "metric": metric,
            "value": value,
            "ci_lower": None,
            "ci_upper": None,
            "n": n,
            "status": status,
            "suppressed_in_reports": suppressed,
        }

    # === Export Methods ===

    def to_html(
        self,
        path: str | Path,
        open_browser: bool = False,
        persona: OutputPersona | str = OutputPersona.DATA_SCIENTIST,
        include_optional: bool = False,
    ) -> Path:
        """Export interactive HTML report.

        Van Calster et al. (2025) Metric Display:
        -----------------------------------------
        By default, reports show only RECOMMENDED metrics (AUROC, calibration plot,
        net benefit, risk distribution). Set include_optional=True to also show
        OPTIONAL metrics (Brier score, O:E ratio, sensitivity+specificity, PPV+NPV).

        Args:
            path: Output file path.
            open_browser: Open report in browser after generation.
            persona: Output persona - 'data_scientist' for full technical output
                (default), 'governance' for streamlined 3-5 page summary.
            include_optional: If True, include Van Calster OPTIONAL metrics in
                data scientist reports. Ignored for governance persona.

        Returns:
            Path to generated report.

        Example:
            # Full report with RECOMMENDED metrics only (new default)
            results.to_html("report.html")

            # Full report with RECOMMENDED + OPTIONAL metrics
            results.to_html("report.html", include_optional=True)

            # Streamlined governance report (RECOMMENDED only, always)
            results.to_html("governance.html", persona="governance")
        """
        from faircareai.reports.generator import (
            generate_governance_html_report,
            generate_html_report,
        )

        path = Path(path)
        persona = _normalize_persona(persona)

        # Create metric display config based on persona and options
        if persona == OutputPersona.GOVERNANCE:
            metric_config = MetricDisplayConfig.governance()
            generate_governance_html_report(self, path, metric_config=metric_config)
        else:
            metric_config = MetricDisplayConfig.data_scientist(include_optional=include_optional)
            generate_html_report(self, path, metric_config=metric_config)

        if open_browser:
            import webbrowser

            webbrowser.open(path.absolute().as_uri())

        return path

    def to_pdf(
        self,
        path: str | Path,
        persona: OutputPersona | str = OutputPersona.DATA_SCIENTIST,
        include_optional: bool = False,
    ) -> Path:
        """Export PDF report.

        Van Calster et al. (2025) Metric Display:
        -----------------------------------------
        By default, reports show only RECOMMENDED metrics (AUROC, calibration plot,
        net benefit, risk distribution). Set include_optional=True to also show
        OPTIONAL metrics (Brier score, O:E ratio, sensitivity+specificity, PPV+NPV).

        Args:
            path: Output file path.
            persona: Output persona - 'data_scientist' for full technical output
                (default), 'governance' for streamlined 3-5 page summary.
            include_optional: If True, include Van Calster OPTIONAL metrics in
                data scientist reports. Ignored for governance persona.

        Returns:
            Path to generated report.

        Example:
            # Full report with RECOMMENDED metrics only (new default)
            results.to_pdf("report.pdf")

            # Full report with RECOMMENDED + OPTIONAL metrics
            results.to_pdf("report.pdf", include_optional=True)

            # Streamlined governance report (RECOMMENDED only, always)
            results.to_pdf("governance.pdf", persona="governance")
        """
        from faircareai.reports.generator import (
            generate_governance_pdf_report,
            generate_pdf_report,
        )

        path = Path(path)
        persona = _normalize_persona(persona)

        # Create metric display config based on persona and options
        if persona == OutputPersona.GOVERNANCE:
            metric_config = MetricDisplayConfig.governance()
            return generate_governance_pdf_report(self, path, metric_config=metric_config)
        else:
            metric_config = MetricDisplayConfig.data_scientist(include_optional=include_optional)
            # Convert AuditResults to AuditSummary for generator, but also pass full results for charts
            summary = self._to_audit_summary()
            return generate_pdf_report(summary, path, metric_config=metric_config, results=self)

    def to_pptx(
        self,
        path: str | Path,
        persona: OutputPersona | str = OutputPersona.DATA_SCIENTIST,  # noqa: ARG002
        include_charts: bool = True,
        pptx_options: "PptxOptions | None" = None,
    ) -> Path:
        """Export PowerPoint deck for governance review.

        Creates a presentation suitable for board meetings and
        governance committee presentations.

        Note:
            The persona parameter is accepted for API consistency but currently
            has no effect - PPTX output is already governance-focused.

        Args:
            path: Output file path.
            persona: Output persona (currently unused - PPTX is governance-focused).
            include_charts: If True, embed key charts in the deck when possible.
            pptx_options: Optional PptxOptions to customize slide order and content.

        Returns:
            Path to generated presentation.

        Example:
            results.to_pptx("report.pptx")
        """
        from faircareai.reports.generator import generate_pptx_report

        path = Path(path)
        # PPTX is already governance-focused, use same generator for all personas
        summary = self._to_audit_summary()
        return generate_pptx_report(
            summary,
            path,
            results=self,
            include_charts=include_charts,
            pptx_options=pptx_options,
        )

    # === Convenience Methods for Governance Persona ===

    def to_governance_html(self, path: str | Path, open_browser: bool = False) -> Path:
        """Export streamlined HTML report for governance committees.

        Shorthand for: results.to_html(path, persona='governance')

        Args:
            path: Output file path.
            open_browser: Open report in browser after generation.

        Returns:
            Path to generated report.
        """
        return self.to_html(path, open_browser=open_browser, persona=OutputPersona.GOVERNANCE)

    def to_governance_pdf(self, path: str | Path) -> Path:
        """Export streamlined PDF report for governance committees.

        Shorthand for: results.to_pdf(path, persona='governance')

        Args:
            path: Output file path.

        Returns:
            Path to generated report.
        """
        return self.to_pdf(path, persona=OutputPersona.GOVERNANCE)

    def to_json(self, path: str | Path) -> Path:
        """Export metrics as JSON for programmatic use.

        Args:
            path: Output file path.

        Returns:
            Path to generated JSON file.
        """
        path = Path(path)

        export_data = {
            "audit_metadata": {
                "audit_id": self.audit_id,
                "run_timestamp": self.run_timestamp,
                "random_seed": self.random_seed,
            },
            "reproducibility": self.reproducibility,
            "config": {
                "model_name": self.config.model_name,
                "model_version": self.config.model_version,
                "primary_fairness_metric": (
                    self.config.primary_fairness_metric.value
                    if self.config.primary_fairness_metric
                    else None
                ),
                "fairness_justification": self.config.fairness_justification,
                "use_case_type": (
                    self.config.use_case_type.value if self.config.use_case_type else None
                ),
                "thresholds": self.config.thresholds,
            },
            "descriptive_stats": self.descriptive_stats,
            "overall_performance": _make_json_serializable(self.overall_performance),
            "subgroup_performance": _make_json_serializable(self.subgroup_performance),
            "fairness_metrics": _make_json_serializable(self.fairness_metrics),
            "intersectional": _make_json_serializable(self.intersectional),
            "flags": self.flags,
            "governance_recommendation": self.governance_recommendation,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return path

    def to_reproducibility_bundle(self, path: str | Path) -> Path:
        """Export reproducibility bundle (environment + run metadata).

        Args:
            path: Output file path.

        Returns:
            Path to generated JSON file.
        """
        path = Path(path)

        export_data = {
            "audit_metadata": {
                "audit_id": self.audit_id,
                "run_timestamp": self.run_timestamp,
                "random_seed": self.random_seed,
            },
            "reproducibility": self.reproducibility,
            "config": {
                "model_name": self.config.model_name,
                "model_version": self.config.model_version,
                "primary_fairness_metric": (
                    self.config.primary_fairness_metric.value
                    if self.config.primary_fairness_metric
                    else None
                ),
                "fairness_justification": self.config.fairness_justification,
                "use_case_type": (
                    self.config.use_case_type.value if self.config.use_case_type else None
                ),
                "thresholds": self.config.thresholds,
                "decision_thresholds": self.config.decision_thresholds,
            },
            "run_parameters": {
                "threshold": self.threshold,
            },
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return path

    def to_model_card(self, path: str | Path) -> Path:
        """Export a governance-focused model card (Markdown)."""
        from faircareai.reports.model_card import generate_model_card_markdown

        return generate_model_card_markdown(self, path)

    def to_structured_model_card(self, path: str | Path) -> Path:
        """Export an AI model card as XML (v0.1 schema)."""
        from faircareai.reports.structured_model_card import generate_model_card_xml

        return generate_model_card_xml(self, path)

    def to_structured_model_card_json(self, path: str | Path) -> Path:
        """Export an AI model card as JSON (debug/reference)."""
        from faircareai.reports.structured_model_card import generate_model_card_json

        return generate_model_card_json(self, path)

    def to_regulatory_checklist(self, path: str | Path) -> Path:
        """Export a regulatory checklist JSON file."""
        from faircareai.reports.regulatory_checklist import generate_regulatory_checklist

        return generate_regulatory_checklist(self, path)

    def to_png(
        self,
        path: str | Path,
        persona: OutputPersona | str = OutputPersona.GOVERNANCE,
        include_optional: bool = False,
        scale: int = 2,
    ) -> Path:
        """Export figures as PNGs (directory or .zip bundle)."""
        from faircareai.reports.figure_exports import export_png_bundle

        persona = _normalize_persona(persona)
        return export_png_bundle(
            self,
            path,
            persona=persona,
            include_optional=include_optional,
            scale=scale,
        )

    def _to_audit_summary(self) -> "AuditSummary":
        """Convert to legacy AuditSummary for report generator compatibility."""
        from faircareai.reports.generator import AuditSummary

        # Get worst disparity
        worst_group = ""
        worst_metric = ""
        worst_value = 0.0

        for attr_name, metrics in self.fairness_metrics.items():
            if not isinstance(metrics, dict):
                continue
            if "equalized_odds_diff" in metrics:
                eo_diffs = metrics["equalized_odds_diff"]
                if not isinstance(eo_diffs, dict):
                    continue
                for group, diff in eo_diffs.items():
                    if str(group) in {str(item) for item in metrics.get("suppressed_groups", [])}:
                        continue
                    # Skip None values
                    if diff is None:
                        continue
                    if abs(diff) > abs(worst_value):
                        worst_group = f"{attr_name}:{group}"
                        worst_metric = "equalized_odds"
                        worst_value = diff

        # Count groups - handle nested structure
        n_groups = 0
        for _attr_name, metrics in self.subgroup_performance.items():
            if isinstance(metrics, dict):
                # Get groups from nested structure
                groups = metrics.get("groups", metrics)
                n_groups += len(
                    [
                        k
                        for k in groups
                        if k not in ("reference", "attribute", "threshold")
                        and not (
                            isinstance(groups.get(k), dict)
                            and groups[k].get("suppressed_in_reports", False)
                        )
                    ]
                )

        return AuditSummary(
            model_name=self.config.model_name,
            audit_date=self.config.report_date or date.today().isoformat(),
            n_samples=self.descriptive_stats.get("cohort_overview", {}).get("n_total", 0),
            n_groups=n_groups,
            threshold=self.threshold,
            pass_count=self.governance_recommendation.get("n_pass", 0),
            warn_count=self.governance_recommendation.get("n_warnings", 0),
            fail_count=self.governance_recommendation.get("n_errors", 0),
            worst_disparity_group=worst_group,
            worst_disparity_metric=worst_metric,
            worst_disparity_value=worst_value,
            metrics_df=pl.DataFrame(),  # Would need to reconstruct
            disparities_df=pl.DataFrame(),  # Would need to reconstruct
        )


def _normalize_persona(persona: OutputPersona | str) -> OutputPersona:
    """Normalize persona parameter to OutputPersona enum.

    Args:
        persona: Persona as enum or string.

    Returns:
        OutputPersona enum value.

    Raises:
        ValueError: If persona string is not recognized.
    """
    if isinstance(persona, OutputPersona):
        return persona
    if isinstance(persona, str):
        persona_lower = persona.lower().replace("-", "_")
        if persona_lower in ("data_scientist", "datascientist", "full", "technical"):
            return OutputPersona.DATA_SCIENTIST
        if persona_lower in ("governance", "executive", "summary", "streamlined"):
            return OutputPersona.GOVERNANCE
        raise ValueError(f"Unknown persona '{persona}'. Use 'data_scientist' or 'governance'.")
    raise TypeError(f"persona must be OutputPersona or str, got {type(persona)}")


def _make_json_serializable(obj: Any) -> Any:
    """Convert objects to JSON-serializable format."""
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(v) for v in obj]
    elif isinstance(obj, pl.DataFrame):
        return obj.to_dicts()
    elif isinstance(obj, pl.Series):
        return obj.to_list()  # Series uses to_list(), not to_dicts()
    elif hasattr(obj, "tolist"):  # numpy arrays
        return obj.tolist()
    elif hasattr(obj, "item"):  # numpy scalars
        return obj.item()
    else:
        return obj


def _as_float(value: Any) -> float | None:
    """Return finite numeric values while excluding booleans and containers."""
    if isinstance(value, (bool, dict, list, tuple)) or value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if np.isfinite(numeric) else None


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def _as_string(value: Any) -> str | None:
    return None if value is None else str(value)


def _ci_bounds(value: Any) -> tuple[float | None, float | None]:
    if not isinstance(value, (list, tuple, np.ndarray)) or len(value) < 2:
        return None, None
    return _as_float(value[0]), _as_float(value[1])


def _is_metadata_metric(metric: str) -> bool:
    return metric.endswith(("_ci", "_ci_95", "_ci_fmt", "_fmt")) or metric in {
        "attribute",
        "reference",
        "threshold",
        "is_reference",
        "small_sample_warning",
    }
