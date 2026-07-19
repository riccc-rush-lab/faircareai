"""Run with: marimo edit notebooks/marimo_quickstart.py."""

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from faircareai import FairCareAudit
    from faircareai.data.synthetic import generate_icu_mortality_data

    return FairCareAudit, generate_icu_mortality_data, mo


@app.cell
def _(mo):
    mo.md(
        """
        # FairCare marimo quickstart

        Install the package with `pip install faircare marimo`, then run this
        file with `marimo edit notebooks/marimo_quickstart.py`.

        FairCare is the package name; `faircareai` is the Python import and CLI.
        This example uses synthetic data only.
        """
    )
    return


@app.cell
def _(FairCareAudit, generate_icu_mortality_data):
    predictions = generate_icu_mortality_data(n_samples=2_000, seed=42)
    audit = FairCareAudit(
        predictions,
        pred_col="prediction",
        target_col="mortality",
        auto_accept=True,
    )
    results = audit.run(fast=True)
    return results,


@app.cell
def _(results):
    results.show(platform="marimo")
    return


@app.cell
def _(mo, results):
    # Aggregate-only, presentation-safe tables are available for custom layouts.
    tables = results.to_tables()
    mo.output.append(mo.ui.table(tables["subgroups"].to_pandas(), selection=None))
    return


@app.cell
def _(mo):
    export = mo.ui.button(label="Export HTML and JSON artifacts")
    mo.output.append(export)
    return export,


@app.cell
def _(export, mo, results):
    if export.value:
        paths = results.save_artifacts("faircare_artifacts", formats=("html", "json"))
        mo.output.append(mo.md(f"Saved aggregate artifacts to `{paths['html'].parent}`."))
    return


if __name__ == "__main__":
    app.run()
