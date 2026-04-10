#!/usr/bin/env python3
"""
FairCareAI Persona Output Demo

Demonstrates the two output personas:
- Data Scientist: Full technical report for model validation
- Governance: Streamlined 3-5 page report for committee review

Usage:
    python examples/persona_demo.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel

from faircareai import FairCareAudit, FairnessConfig, FairnessMetric, UseCaseType
from faircareai.data.synthetic import generate_icu_mortality_data


def main():
    """Demonstrate both output personas."""
    console = Console()
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    console.print(Panel.fit(
        "[bold blue]FairCareAI Output Personas Demo[/bold blue]\n"
        "Comparing Data Scientist vs Governance output formats",
        border_style="blue",
    ))
    console.print()

    # Generate synthetic data
    console.print("[bold]1. Creating sample data...[/bold]")
    df = generate_icu_mortality_data(n_samples=1500, seed=42)
    console.print(f"   Generated {len(df):,} patient records\n")

    # Run audit
    console.print("[bold]2. Running fairness audit...[/bold]")
    audit = FairCareAudit(
        data=df,
        pred_col="y_prob",
        target_col="y_true",
        threshold=0.5,
    )

    # Configure sensitive attributes
    audit.accept_suggested_attributes([0, 1])  # race, insurance

    audit.config = FairnessConfig(
        model_name="Readmission Risk v2.0",
        model_version="2.0.0",
        intended_use="Identify patients at high risk for 30-day readmission",
        intended_population="Adult inpatients discharged from medicine service",
        primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
        fairness_justification=(
            "Model triggers care management outreach. Equalized odds ensures "
            "equal opportunity for beneficial intervention across groups."
        ),
        use_case_type=UseCaseType.INTERVENTION_TRIGGER,
    )

    results = audit.run(bootstrap_ci=True, n_bootstrap=200)
    console.print("   Audit complete!\n")

    # Show summary
    gov = results.governance_recommendation
    n_outside = gov.get('outside_threshold_count', gov.get('n_errors', 0))
    n_near = gov.get('near_threshold_count', gov.get('n_warnings', 0))
    n_within = gov.get('within_threshold_count', gov.get('n_pass', 0))

    if n_outside > 0:
        status = "REVIEW NEEDED"
    elif n_near > 0:
        status = "CONDITIONAL"
    else:
        status = "READY"

    console.print(f"   Status: [bold]{status}[/bold]")
    console.print(f"   Within threshold: {n_within} | Near: {n_near} | Outside: {n_outside}\n")

    # Export Data Scientist reports
    console.print("[bold]3. Exporting Data Scientist reports...[/bold]")
    console.print("   (Full technical output for model validation)")

    ds_html = output_dir / "data_scientist_report.html"
    results.to_html(ds_html)
    console.print(f"   ✓ HTML: {ds_html}")

    console.print()

    # Export Governance reports
    console.print("[bold]4. Exporting Governance reports...[/bold]")
    console.print("   (Streamlined 3-5 page output for committee review)")

    gov_html = output_dir / "governance_report.html"
    results.to_governance_html(gov_html)
    console.print(f"   ✓ HTML: {gov_html}")

    # Also show the alternative syntax
    gov_html_alt = output_dir / "governance_report_alt.html"
    results.to_html(gov_html_alt, persona="governance")
    console.print(f"   ✓ HTML (alt syntax): {gov_html_alt}")

    console.print()

    # Show the API
    console.print("[bold]5. API Reference[/bold]\n")
    console.print(Panel.fit("""[cyan]# Data Scientist (default) - Full technical output[/cyan]
results.to_html("report.html")
results.to_pdf("report.pdf")

[cyan]# Governance - Streamlined for committees[/cyan]
results.to_html("gov.html", persona="governance")
results.to_pdf("gov.pdf", persona="governance")
results.to_pptx("gov.pptx")  # Always governance-focused

[cyan]# Convenience shortcuts[/cyan]
results.to_governance_html("gov.html")
results.to_governance_pdf("gov.pdf")""",
        title="Export Methods",
        border_style="cyan",
    ))

    console.print()
    console.print("[bold green]Done![/bold green] Check the 'output/' folder for reports.")
    console.print()

    # File comparison
    ds_size = ds_html.stat().st_size if ds_html.exists() else 0
    gov_size = gov_html.stat().st_size if gov_html.exists() else 0

    console.print("[dim]File sizes:[/dim]")
    console.print(f"  Data Scientist HTML: {ds_size:,} bytes")
    console.print(f"  Governance HTML:     {gov_size:,} bytes")
    console.print(f"  Ratio: Governance is ~{gov_size/ds_size*100:.0f}% of full report")


if __name__ == "__main__":
    main()
