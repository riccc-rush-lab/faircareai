# Microsoft Fabric and Databricks notebooks

For the installation matrix and Jupyter/marimo quickstarts, start with
[NOTEBOOKS.md](NOTEBOOKS.md). This guide is the detailed PySpark reference.

In Fabric or Databricks, install the published package with `%pip install faircare`
and restart the notebook session before importing it. PySpark is supplied by the
managed platform and is not installed by FairCare.

FairCareAI accepts a batch PySpark DataFrame directly. It selects only the
prediction, outcome, detected demographic, explicitly configured sensitive,
and `spark_extra_columns` fields. Before collecting, it persists the narrow
projection and checks `max_collect_rows + 1`, so an unexpectedly large input
fails before driver collection.

```python
from faircareai import FairCareAudit, FairnessConfig, FairnessMetric

audit = FairCareAudit(
    spark_df,
    pred_col="risk_score",
    target_col="readmit_30d",
    sensitive_attrs={"race": "race", "insurance": "payor"},
    max_collect_rows=500_000,
    config=FairnessConfig(
        model_name="Readmission model",
        primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
        fairness_justification="The model triggers outreach, so both missed benefit and false-alarm burden matter.",
    ),
)
results = audit.run(fast=True)
```

`show=True` renders a summary, stable Polars tables, and Plotly figures using
the notebook's native display path. It does not save data. You can call the
display API again with selected sections:

```python
results.show(sections=["summary", "overall", "subgroups", "disparities", "calibration", "flags", "figures"])
results.show(platform="fabric", max_rows=200, plotlyjs="inline")
results.show(platform="databricks", max_rows=200, plotlyjs="cdn")
```

For programmatic access, use `results.to_tables()` or
`results.to_metrics_frame()`. These contain aggregate audit results, not the
patient-level source rows.

## Save files

```python
# Microsoft Fabric Lakehouse Files
fabric_paths = results.save_artifacts(
    "/lakehouse/default/Files/faircare/audits",
    formats=("html", "json"),
)

# Databricks Unity Catalog Volume
databricks_paths = results.save_artifacts(
    "/Volumes/catalog/schema/governance/faircare/audits",
    formats=("html", "json"),
)
```

Each call creates an `audit_id` subdirectory and refuses to replace existing
artifacts unless `overwrite=True` is passed.

## Save a queryable Delta history

```python
results.save_delta(spark, "governance.faircare_audit_metrics", mode="append")
```

The Delta table uses a stable long-form schema with audit metadata, section,
attribute, group, metric, value, confidence bounds, sample size, status, and a
small-cell suppression marker. Append mode rejects a duplicate `audit_id`.

## Operational limits

- Streaming DataFrames must first be materialized as a bounded batch.
- Array, map, and struct inputs must be flattened or cast before collection.
- Increase `max_collect_rows` deliberately only after checking driver memory.
- Human-facing tables and subgroup figures suppress cells below the configured
  `suppress_cell_n`; machine-readable results retain values plus the marker.
