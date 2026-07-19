# Notebook environments

FairCare uses one package name in installers and another in Python:

```bash
pip install faircare
```

```python
from faircareai import FairCareAudit
```

The `faircareai` command is also the installed CLI. Notebook hosts and PySpark
remain host-owned optional dependencies: installing FairCare does not install a
Spark runtime or a notebook server.

| Environment | Install FairCare | Display call | Notes |
| --- | --- | --- | --- |
| Jupyter | `pip install faircare` | `results.show(platform="jupyter")` | Install JupyterLab separately if it is not already available. |
| marimo | `pip install faircare marimo` | `results.show(platform="marimo")` | Marimo is optional and is not installed by FairCare. |
| Microsoft Fabric | `%pip install faircare` | `results.show(platform="fabric")` | Restart the notebook session after installation. PySpark is provided by Fabric. |
| Databricks | `%pip install faircare` | `results.show(platform="databricks")` | Restart Python after installation. PySpark is provided by Databricks. |

Use `pip install "faircare[export]"` when the notebook must create PDF, PPTX,
or PNG artifacts. HTML and JSON artifacts do not need that extra.

## Jupyter

Use the checked-in [quickstart notebook](../notebooks/quickstart_tutorial.ipynb)
or begin with a local DataFrame or file:

```python
from faircareai import FairCareAudit

audit = FairCareAudit(
    data="predictions.parquet",
    pred_col="risk_score",
    target_col="outcome",
)
audit.suggest_attributes()
audit.accept_suggested_attributes([1])
results = audit.run()
results.show(platform="jupyter", max_rows=200)
```

`show()` renders aggregate tables and Plotly figures; it does not persist any
files. Use `results.to_tables()` for presentation-safe aggregate tables or
`results.to_metrics_frame()` for the normalized aggregate metric table.

## marimo

The git-friendly [marimo quickstart](../notebooks/marimo_quickstart.py) is a
runnable application:

```bash
pip install faircare
pip install marimo
marimo edit notebooks/marimo_quickstart.py
```

Use `results.show(platform="marimo")` inside a marimo cell. FairCare appends
Markdown, interactive tables, and Plotly output through marimo's native output
APIs. Calling that platform without marimo installed raises an error with the
required install command.

## Microsoft Fabric and Databricks (PySpark)

Use a **batch** PySpark DataFrame and follow the canonical
[Spark notebook guide](SPARK_NOTEBOOKS.md) for the constructor, native display,
Fabric Lakehouse/Databricks Volume artifact paths, and Delta history. It explains
how `max_collect_rows` bounds driver collection and how `save_delta()` persists
aggregate metrics only; source patient-level rows are never written.
