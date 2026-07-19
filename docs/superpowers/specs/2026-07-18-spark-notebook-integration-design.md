# Spark Notebook Integration Design

**Status:** Approved
**Date:** 2026-07-18
**Target release:** FairCareAI v0.3.0

## Problem

`FairCareAudit.run()` returns an `AuditResults` object but does not render it. Assigning that
object in a Microsoft Fabric or Databricks PySpark notebook therefore appears to do nothing.
The package also cannot accept a PySpark DataFrame directly, and its file exports do not explain
which persistent notebook paths to use.

The integration must make the notebook happy path visible, accept guarded Spark input without
rewriting the metric engine, and persist both human-readable artifacts and queryable metrics.

## Goals

- Accept PySpark DataFrames from Fabric and Databricks without making PySpark a required package
  dependency.
- Prevent accidental, unbounded collection of distributed data onto the Spark driver.
- Render useful tables and interactive figures through the notebook's native display functions.
- Save reports to Fabric Lakehouse Files or Databricks Unity Catalog Volumes.
- Append normalized audit metrics to a Delta table for longitudinal analysis and BI.
- Preserve existing Polars, pandas, CSV, and Parquet behavior.

## Non-goals

- Reimplement FairCareAI's metrics or bootstraps as distributed Spark algorithms.
- Accept streaming DataFrames.
- Automatically create Fabric Lakehouses, Databricks catalogs, schemas, or volumes.
- Persist patient-level prediction or sensitive-attribute data in result artifacts.
- Use DBFS root or legacy DBFS mounts as a recommended Databricks destination.

## Architecture

The implementation has three bounded units:

1. A Spark input adapter converts a deliberately narrow Spark projection to pandas with Arrow,
   then to the existing Polars representation.
2. A notebook display adapter renders normalized result tables and existing Plotly figures using
   the host notebook's `display` and `displayHTML` hooks.
3. Result persistence writes report artifacts through ordinary POSIX paths and normalized metrics
   through the caller's Spark session.

Platform-specific code stays out of metric computation. Imports of PySpark, IPython, Fabric
`notebookutils`, and Databricks utilities are lazy so normal Python installations remain unchanged.

## Public API

### Spark input

`FairCareAudit.__init__` includes the v0.3 sensitive-attribute options and gains two Spark-specific
keyword-only parameters:

```python
FairCareAudit(
    data,
    pred_col: str,
    target_col: str,
    config: FairnessConfig | None = None,
    threshold: float = 0.5,
    *,
    sensitive_attrs: dict[str, str] | None = None,
    auto_accept: bool = False,
    include_unknown: bool = True,
    max_collect_rows: int = 500_000,
    spark_extra_columns: Sequence[str] | None = None,
)
```

For Spark input, the adapter selects only:

- `pred_col` and `target_col`;
- columns matching FairCareAI's sensitive-attribute detection patterns;
- columns named by constructor-level `sensitive_attrs`; and
- `spark_extra_columns`, for custom attributes registered after construction.

The adapter validates all selected names before starting a Spark action. A later call to
`add_sensitive_attribute()` for a Spark column that was not collected raises an error explaining
that it must be supplied through `sensitive_attrs` or `spark_extra_columns`.

The selected DataFrame is persisted with `MEMORY_AND_DISK`, evaluated with
`limit(max_collect_rows + 1).count()`, converted with Arrow-enabled `toPandas()`, and unpersisted in
a `finally` block. More than `max_collect_rows` raises `DataValidationError` before collection. The
message reports the limit and instructs the user to filter, aggregate, or deliberately choose a
higher positive limit. Streaming DataFrames and selected array, map, or struct columns are rejected.

### Notebook display

`FairCareAudit.run()` gains an opt-in convenience argument:

```python
audit.run(..., show: bool = False) -> AuditResults
```

When true, it calls `results.show()` only after a successful audit. The default remains false so
scripts, scheduled notebooks, pipelines, and tests do not acquire display side effects.

`AuditResults` gains:

```python
results.show(
    sections: str | Sequence[str] = "all",
    *,
    persona: OutputPersona | str = "data_scientist",
    platform: Literal["auto", "fabric", "databricks", "jupyter"] = "auto",
    max_rows: int = 1_000,
    plotlyjs: Literal["cdn", "inline"] = "cdn",
) -> AuditResults

results.to_tables() -> dict[str, polars.DataFrame]
```

Supported section names are `summary`, `overall`, `subgroups`, `disparities`, `calibration`,
`flags`, and `figures`. `all` renders them in that order. Unknown names fail before output begins.
`max_rows` must be between 1 and 10,000, matching Fabric's documented notebook display ceiling.

`to_tables()` returns small, presentation-ready Polars DataFrames with stable schemas. `show()`
converts each table to pandas for the managed notebook `display` hook. In standard Jupyter it uses
IPython display. In a non-notebook process it prints the summary and table text, then warns that
interactive figures require a notebook or explicit export.

Figures render as Plotly HTML fragments through `displayHTML`. The default `plotlyjs="cdn"` avoids
duplicating several megabytes of JavaScript in every output; `plotlyjs="inline"` supports networks
that block the CDN at the cost of larger notebook output. A `displayHTML` failure identifies the
section and recommends `save_artifacts(..., formats=("html",))`; failures do not silently skip a
figure. The default data-scientist figure set is discrimination, overall calibration, decision
curve, and subgroup comparison. Governance mode uses the executive summary and governance
scorecard.

Automatic platform detection checks Databricks runtime indicators first, then importability of
Fabric `notebookutils`, then IPython. An explicit platform overrides detection. The display adapter
accepts injected display functions internally so behavior can be unit-tested without either cloud
runtime.

### Normalized metrics and persistence

`AuditResults` gains:

```python
results.to_metrics_frame() -> polars.DataFrame

results.save_artifacts(
    destination: str | Path,
    *,
    formats: Sequence[Literal["html", "json", "png", "pdf", "pptx"]] = ("html", "json"),
    persona: OutputPersona | str = "data_scientist",
    overwrite: bool = False,
) -> dict[str, Path]

results.save_delta(
    spark,
    table: str,
    *,
    mode: Literal["append", "error"] = "append",
) -> str
```

`to_metrics_frame()` returns one row per metric with this stable schema:

| Column | Type | Meaning |
| --- | --- | --- |
| `audit_id` | string | FairCareAI run identifier |
| `run_timestamp` | string | ISO-8601 execution time |
| `model_name` | string | Configured model name |
| `model_version` | string | Configured model version |
| `section` | string | Overall, subgroup, disparity, calibration, or flag |
| `attribute` | string nullable | Sensitive attribute |
| `group` | string nullable | Subgroup label |
| `metric` | string | Stable metric key |
| `value` | double nullable | Numeric result |
| `ci_lower` | double nullable | Lower confidence bound |
| `ci_upper` | double nullable | Upper confidence bound |
| `n` | long nullable | Supporting sample count |
| `status` | string nullable | Pass, warn, fail, or informational status |
| `suppressed_in_reports` | boolean | Small-cell reporting marker |

No prediction rows or raw sensitive values beyond already-aggregated group labels enter this frame.

`save_artifacts()` stages every requested artifact in a temporary local directory, then copies
completed files to the destination. This supports `/lakehouse/default/Files/...` in an attached
Fabric Lakehouse and `/Volumes/<catalog>/<schema>/<volume>/...` in Databricks. It creates the final
audit-ID subdirectory, refuses existing files unless `overwrite=True`, and returns the final paths.
Format-specific optional-dependency errors retain the package's existing installation guidance.

`save_delta()` creates a Spark DataFrame from `to_metrics_frame()` and writes Delta through
`saveAsTable(table)`. `append` rejects an existing copy of the same `audit_id` to prevent accidental
duplication. `error` requires the destination table not to exist. The table name is always supplied
by the caller because the package must not guess Fabric schemas or Databricks catalog permissions.
Recomputed audits receive a new audit ID and are appended as a new run; v0.3 does not mutate
previously persisted audit rows.

## User experience

Fabric:

```python
audit = FairCareAudit(spark_df, "risk_score", "outcome")
results = audit.run(show=True)

paths = results.save_artifacts(
    "/lakehouse/default/Files/faircare/audits",
    formats=("html", "json", "png"),
)
results.save_delta(spark, "dbo.faircare_audit_metrics")
```

Databricks:

```python
audit = FairCareAudit(spark_df, "risk_score", "outcome")
results = audit.run()
results.show()

paths = results.save_artifacts(
    "/Volumes/main/clinical/faircare/audits",
    formats=("html", "json", "png"),
)
results.save_delta(spark, "main.clinical.faircare_audit_metrics")
```

After a normal `run(show=False)`, the completion message tells notebook users to call
`results.show()`, `results.save_artifacts(...)`, or `results.save_delta(...)`.

## Error handling

- Spark collection errors name the row limit and selected columns and do not expose data values.
- Missing or unsupported Spark columns fail before collection.
- Display errors identify the failed section while leaving the result object usable.
- Artifact creation is all-or-nothing per file: partially generated files never appear at the final
  destination.
- Existing artifacts are protected by default.
- Delta writes validate the table identifier and duplicate audit ID before mutation.

## Testing

- Use lightweight fake Spark objects for projection, limit, count, persistence, conversion, and
  cleanup tests; add optional integration tests when PySpark is installed.
- Verify only required columns are collected and excess rows, streaming frames, complex types,
  missing columns, invalid limits, and conversion failures produce actionable errors.
- Test platform detection order, explicit overrides, injected display functions, section ordering,
  max-row validation, terminal fallback, and figure failure messages.
- Snapshot the normalized table schemas and representative metric rows, including null confidence
  intervals and small-cell markers.
- Test Fabric and Databricks destination shapes with temporary POSIX stand-ins, including directory
  creation, collision protection, overwrite behavior, and cleanup after failed generation.
- Test Delta append, duplicate-audit rejection, absent-table error mode, and writer failures through
  a fake Spark writer plus an optional local Delta integration test.
- Add documented Fabric and Databricks quick-start notebooks and smoke-test their source cells for
  current public API usage.

## Documentation references

- Microsoft Fabric notebook tables, `displayHTML`, and Plotly:
  <https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-visualization>
- Microsoft Fabric attached-Lakehouse file paths:
  <https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook>
- Databricks Spark-to-pandas driver collection:
  <https://docs.databricks.com/aws/en/pandas/pyspark-pandas-conversion>
- Databricks Unity Catalog Volume storage recommendations:
  <https://docs.databricks.com/aws/en/files/files-recommendations>
- Databricks notebook HTML display:
  <https://docs.databricks.com/aws/en/notebooks/notebook-media>
