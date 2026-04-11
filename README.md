# FairCareAI

[![CI](https://github.com/riccc-rush-lab/faircareai/actions/workflows/ci.yml/badge.svg)](https://github.com/riccc-rush-lab/faircareai/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/faircare.svg)](https://pypi.org/project/faircare/)
[![Downloads](https://img.shields.io/pypi/dm/faircare.svg)](https://pypi.org/project/faircare/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG-2.1%20AA-green.svg)](https://www.w3.org/WAI/WCAG21/quickref/)

**Fairness auditing for healthcare AI — from model predictions to governance-ready reports in minutes.**

---

## Why FairCareAI Exists

Healthcare AI models can quietly harm patients when overall performance masks meaningful differences across patient subgroups. A model that looks strong in aggregate may perform substantially worse for certain populations — and those gaps are invisible without deliberate measurement.

Most hospitals have no standardized way to detect, quantify, or present these disparities to governance committees. Data scientists know the statistics but lack tools to produce the publication-ready, plain-language reports that clinical leadership needs to make deployment decisions.

**FairCareAI closes that gap.** It takes your model's predictions and produces a complete fairness audit — discrimination, calibration, clinical utility, and subgroup analysis — with two output modes: full technical reports for data scientists, and streamlined 3-5 page reports for governance committees.

---

## Who This Package Is For

| Role | What FairCareAI gives you |
|------|---------------------------|
| **Hospital data scientists** | Automated fairness metrics (AUROC, calibration, DCA) with bootstrap confidence intervals, exportable as HTML/PDF/PPTX |
| **Clinical informaticists** | Governance-ready reports with plain-language explanations suitable for IRB, ethics committees, or C-suite review |
| **Governance committees** | Clear pass/warning/flag indicators, sign-off workflows, and audit trail documentation |
| **Health equity researchers** | Publication-ready figures (WCAG 2.1 AA, colorblind-safe, 14px minimum) with full methodology citations |
| **Regulatory & compliance teams** | Structured model cards, responsible AI checklists, and reproducibility bundles |

---

## How It Works

```bash
pip install faircare
```

```python
from faircareai import FairCareAudit, FairnessConfig, FairnessMetric

# Point at your model's predictions
audit = FairCareAudit(data="predictions.parquet", pred_col="risk_score", target_col="readmit_30d")

# Detect and accept demographic columns
audit.suggest_attributes()
audit.accept_suggested_attributes([1, 2, 3])  # e.g., race, sex, insurance

# Configure and run
audit.config = FairnessConfig(
    model_name="Readmission Risk Model v2",
    primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
    fairness_justification="Model triggers intervention; equal TPR/FPR ensures equitable access.",
)
results = audit.run()

# Export
results.to_html("technical_report.html")                      # Full data scientist report
results.to_governance_pdf("governance_report.pdf")             # 3-5 page governance summary
results.to_pptx("committee_deck.pptx")                        # PowerPoint for meetings
```

> **All outputs are advisory.** Final deployment decisions rest with clinical stakeholders and governance committees who understand the local context.

---

## Key Features

- **Two output personas** — Full technical reports for data scientists, streamlined 3-5 page reports for governance committees
- **Discrimination, calibration & clinical utility** — AUROC, calibration curves, Brier score, decision curve analysis, and classification metrics at your chosen threshold
- **Subgroup fairness analysis** — Performance broken down by race, sex, insurance, age, language, and custom attributes
- **Plain-language explanations** — Every visualization includes clear explanations of what the metric means and why it matters
- **Multiple export formats** — HTML, PDF, PowerPoint, PNG bundles, JSON, model cards, reproducibility bundles
- **Publication-ready** — Minimum 14px fonts, WCAG 2.1 AA compliant, colorblind-safe Okabe-Ito palette
- **HIPAA-friendly** — All computation runs locally, no cloud dependencies, no data leaves your machine
- **Interactive dashboard** — Streamlit UI for upload, analysis, and export without writing code

---

## Installation

### Basic Installation

```bash
pip install faircare
```

### With Export Capabilities (PDF/PPTX)

```bash
pip install "faircare[export]"
python -m playwright install chromium  # Required for PDF generation
```

**Note**: PDF generation uses Playwright for cross-platform compatibility. See [docs/PDF_SETUP_GUIDE.md](docs/PDF_SETUP_GUIDE.md) for details.

PNG export uses Kaleido for static Plotly rendering (included in `faircare[export]`).

### With Compliance Validation (XML Schema)

```bash
pip install "faircare[compliance]"
```

Installs `xmlschema` to validate model card XML against the v0.1 XSD.

### Development Installation

```bash
git clone https://github.com/riccc-rush-lab/faircareai.git
cd faircareai
uv sync --extra dev
pre-commit install
```

### Platform Support

FairCareAI is tested and supported on:

| Platform | Python Versions | Status |
|----------|-----------------|--------|
| **macOS** (Intel & Apple Silicon) | 3.10, 3.11, 3.12 | ✅ Fully Supported |
| **Windows** (x64) | 3.10, 3.11, 3.12 | ✅ Fully Supported |
| **Linux** (Ubuntu, Debian, RHEL, Arch) | 3.10, 3.11, 3.12 | ✅ Fully Supported |

**Notes:**
- No system dependencies required beyond Python
- Identical setup on all platforms
- CI/CD tested on all platform combinations

### Requirements

Python >= 3.10. See `pyproject.toml` for the complete dependency list.

---

## Data Requirements

### What You Need to Bring

| Required | Column | Type | Description |
|----------|--------|------|-------------|
| Yes | **Predictions** | float [0.0, 1.0] | Model-generated risk probabilities — use `predict_proba()[:, 1]`, not logits or binary labels |
| Yes | **Outcomes** | int (0 or 1) | Actual binary outcomes from a held-out test set |
| Recommended | **Sensitive attributes** | string/categorical | Demographics — auto-detected from column names or added manually |

### Supported Formats

| Format | Example |
|--------|---------|
| Parquet (recommended) | `FairCareAudit(data="predictions.parquet", ...)` |
| CSV | `FairCareAudit(data="data.csv", ...)` |
| Polars DataFrame | `FairCareAudit(data=pl_df, ...)` |
| Pandas DataFrame | `FairCareAudit(data=pd_df, ...)` |

### Auto-Detected Sensitive Attributes

FairCareAI recognizes common healthcare demographic column names automatically:

| Attribute | Detected column names | Default reference |
|-----------|----------------------|-------------------|
| Race/Ethnicity | `race`, `ethnicity`, `race_eth`, `patient_race`, `race_cd`, `race_ethnicity` | White |
| Sex | `sex`, `gender`, `patient_sex`, `sex_cd`, `birth_sex` | Male |
| Age Group | `age_group`, `age_cat`, `age_bucket`, `age_band`, `age_category` | (largest group) |
| Insurance | `insurance`, `payer`, `insurance_type`, `coverage`, `payer_type`, `payer_category` | Commercial |
| Language | `language`, `primary_language`, `lang`, `language_cd`, `preferred_language` | English |
| Disability | `disability`, `disabled`, `disability_status`, `functional_status` | No |

Add attributes beyond auto-detection with `audit.add_sensitive_attribute()`, or analyze intersections (e.g., race × sex) with `audit.add_intersection(["race", "sex"])`.

### Pre-Audit Checklist

- [ ] Predictions are probabilities in [0.0, 1.0]
- [ ] Outcomes are binary (0 or 1)
- [ ] Data is from a held-out test set (not training data)
- [ ] At least one sensitive attribute column is present
- [ ] Clinical context is defined (threshold, use case type)

---

## Quick Start

```python
from faircareai import FairCareAudit, FairnessConfig, FairnessMetric, UseCaseType

# Load predictions (Parquet, CSV, Polars, or Pandas DataFrame)
audit = FairCareAudit(
    data="predictions.parquet",
    pred_col="risk_score",
    target_col="readmit_30d",
)

# Auto-detect demographic columns and accept them
audit.suggest_attributes()
audit.accept_suggested_attributes([1, 2, 3])  # e.g. race, sex, insurance

# Configure fairness context
audit.config = FairnessConfig(
    model_name="Readmission Risk Model v2.0",
    intended_use="Trigger care management outreach for high-risk patients",
    intended_population="Adult patients discharged from acute care",
    primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
    fairness_justification=(
        "Model triggers a beneficial intervention. Equalized odds ensures "
        "equal TPR/FPR across groups, preventing differential access to care."
    ),
    use_case_type=UseCaseType.INTERVENTION_TRIGGER,
)

# Run the audit
results = audit.run()

# Export: full technical report for data scientists
results.to_html("fairness_report.html")
results.to_pdf("fairness_report.pdf")

# Export: streamlined 3-5 page report for governance committees
results.to_governance_pdf("governance.pdf")
results.to_pptx("committee_deck.pptx")
```

---

## Output Personas

FairCareAI supports two output personas to serve different audiences with tailored content:

### Data Scientist (Default)

**Purpose**: Full technical validation and model documentation
**Audience**: Data scientists, ML engineers, statisticians
**Content**:
- All 7 report sections (Executive Summary, Descriptive Stats, Overall Performance, Subgroup Performance, Fairness Assessment, Flags, Governance Decision)
- All visualizations (~15-20 figures) with complete metric tables and bootstrap confidence intervals
- Technical terminology and statistical detail
- **Length**: 15-20+ pages

**Use when**:
- Documenting model validation for regulatory submission
- Internal technical review and methodology audit
- Research publication and reproducibility
- Detailed debugging of fairness issues

### Governance

**Purpose**: Streamlined executive review for decision-making
**Audience**: Governance committees, clinical leadership, non-technical stakeholders
**Content**:
- 5 key sections (Executive Summary, Overall Performance, Subgroup Performance, Flags, Governance Decision)
- Standard figure set:
  - 4 overall performance figures (AUROC, Calibration, Brier Score, Classification Metrics)
  - 4 subgroup fairness figures per sensitive attribute (AUROC, Sensitivity/TPR, FPR, Selection Rate)
- Plain language summaries with clinical interpretation
- Clear pass/warning/flag indicators
- **Minimum 14px fonts** for readability
- **WCAG 2.1 AA compliant** visualizations
- **Length**: 3-5 pages

**Use when**:
- Preparing materials for governance committee or IRB review
- Briefing clinical leadership or a board
- Seeking clinical deployment approval
- Communicating with non-technical stakeholders

### API Examples

```python
# Data Scientist output (default)
results.to_html("full_report.html")
results.to_pdf("full_report.pdf")

# Governance output (method 1: convenience methods)
results.to_governance_html("governance.html")
results.to_governance_pdf("governance.pdf")

# Governance output (method 2: persona parameter)
results.to_html("governance.html", persona="governance")
results.to_pdf("governance.pdf", persona="governance")

# PowerPoint (always governance-focused)
results.to_pptx("governance_deck.pptx")

# Model card + compliance artifacts
results.to_model_card("model_card.md")
results.to_structured_model_card("model_card.xml")
results.to_structured_model_card_json("model_card.json")
results.to_regulatory_checklist("checklist.json")
results.to_reproducibility_bundle("reproducibility.json")

# CLI reproducibility bundle
# faircareai audit data.csv -p risk -t outcome --format repro-bundle -o repro.json

# PNG bundle of figures
results.to_png("figures.zip", persona="governance")

# Data scientist PNGs with optional metrics
results.to_png("figures_ds.zip", persona="data_scientist", include_optional=True)
```

`to_regulatory_checklist()` exports a structured checklist with criterion IDs and reviewer placeholders to support governance sign-off workflows.

---

## Fairness Visualizations

FairCareAI generates a standard set of visualizations for healthcare AI performance assessment. Each figure includes plain-language explanations suitable for clinical leadership and non-technical reviewers.

### Overall Performance (4 figures)

| Figure | Metric | Clinical interpretation |
|--------|--------|------------------------|
| ROC curve | AUROC | Model's ability to rank patients correctly. 0.7+ acceptable, 0.8+ strong. |
| Calibration curve | Calibration slope | Do predicted probabilities match observed rates? Slope 0.8–1.2 is acceptable. |
| Brier score gauge | Brier score | Overall probabilistic accuracy. <0.15 excellent, 0.15–0.25 acceptable. |
| Classification bar chart | Sensitivity / Specificity / PPV | Tradeoffs at the chosen decision threshold. |

### Subgroup Fairness (4 figures per attribute)

For each sensitive attribute (race, sex, insurance, etc.):

| Figure | Metric | Fairness goal |
|--------|--------|---------------|
| AUROC by group | Discrimination | Group differences < 0.05 |
| Sensitivity (TPR) by group | Detection rate | Group differences < 10 pp |
| FPR by group | False alarm rate | Group differences < 10 pp |
| Selection rate by group | Flagging rate | Clinically justified differences |

### Typography and Accessibility

All visualizations follow publication-ready standards:

- **Minimum 14px font size** for all text (publication-compliant)
- **WCAG 2.1 AA contrast ratios** for text and UI elements
- **Colorblind-safe palettes** (tested with CVD simulation)
- **Alt text** for screen readers on all figures
- **Clear axis labels** with units and context
- **High-resolution export** suitable for print publication

---

## Fairness Metrics

FairCareAI supports multiple fairness definitions. No single metric is universally correct — the fairness impossibility theorem (Chouldechova 2017, Kleinberg et al. 2017) shows that when base rates differ across groups, most fairness criteria cannot all be satisfied simultaneously. Metric selection is a value judgment that must be made in clinical context.

| Metric | Definition | Common Use Case | Clinical Interpretation |
|--------|------------|-----------------|------------------------|
| **Demographic Parity** | Equal selection rates across groups:<br>P(Ŷ=1\|A=a) = P(Ŷ=1\|A=b) | Resource allocation | Equal proportion of each group receives intervention |
| **Equalized Odds** | Equal true/false positive rates across groups:<br>P(Ŷ=1\|Y=y,A=a) = P(Ŷ=1\|Y=y,A=b), for y∈{0,1} | Intervention triggers | Similar missed-case and false-alarm rates across groups |
| **Equal Opportunity** | Equal true positive rates across groups:<br>P(Ŷ=1\|Y=1,A=a) = P(Ŷ=1\|Y=1,A=b) | Screening programs | Similar detection of true cases across groups |
| **Predictive Parity** | Equal positive predictive value across groups:<br>P(Y=1\|Ŷ=1,A=a) = P(Y=1\|Ŷ=1,A=b) | Risk communication | A positive flag has similar meaning across groups |
| **Calibration** | Group-wise risk calibration:<br>E[Y\|R_hat=p,A=a] = p (equivalently, P(Y=1\|R_hat=p,A=a)=p) | Shared decision-making | Predicted risk aligns with observed risk within each group |

### Metric Selection Guidance

Use `audit.suggest_fairness_metric()` for context-specific recommendations based on your use case type:

- **Intervention Trigger** (care management, outreach) → Equalized Odds
- **Risk Communication** (patient counseling) → Calibration
- **Resource Allocation** (limited slots) → Demographic Parity
- **Screening** (disease detection) → Equal Opportunity

---

## Use Cases

### Intervention Trigger Models

Models that determine who receives an intervention (care management, outreach):
- **Recommended metric**: Equalized Odds
- **Key concern**: Equal access to beneficial interventions
- **Example**: Post-discharge care management referral

### Risk Communication

Models that communicate risk to patients/providers:
- **Recommended metric**: Calibration
- **Key concern**: Trustworthy probabilities for shared decisions
- **Example**: 10-year cardiovascular risk calculator

### Resource Allocation

Models that allocate limited resources:
- **Recommended metric**: Demographic Parity
- **Key concern**: Proportional distribution of resources
- **Example**: Care coordination slot assignment

### Screening Programs

Models used for disease screening:
- **Recommended metric**: Equal Opportunity
- **Key concern**: Equal detection rates for those with disease
- **Example**: Diabetic retinopathy screening

---

## API Reference

### Core Classes

#### `FairCareAudit`

Main orchestration class for conducting fairness audits.

```python
audit = FairCareAudit(
    data: pl.DataFrame | pd.DataFrame | str | Path,
    pred_col: str,
    target_col: str,
    config: FairnessConfig | None = None,
    threshold: float = 0.5
)
```

**Key Methods**:

```python
# Attribute management
audit.suggest_attributes() -> list[dict]
audit.accept_suggested_attributes(selections: list[int | str])
audit.add_sensitive_attribute(name, column, reference, categories, clinical_justification)
audit.add_intersection(attributes: list[str])

# Configuration
audit.suggest_fairness_metric() -> dict
audit.config.validate() -> list[str]

# Execution
results = audit.run(bootstrap_ci=True, n_bootstrap=1000) -> AuditResults
```

#### `FairnessConfig`

Configuration for a fairness audit.

```python
config = FairnessConfig(
    model_name: str,                              # Required
    model_version: str = "1.0.0",
    model_type: ModelType = ModelType.BINARY_CLASSIFIER,
    intended_use: str = "",                       # Recommended
    intended_population: str = "",                # Recommended
    primary_fairness_metric: FairnessMetric | None = None,  # Required
    fairness_justification: str = "",             # Required
    use_case_type: UseCaseType | None = None,
    thresholds: dict = {...},                     # Configurable
    decision_thresholds: list[float] = [0.5],
)
```

**Thresholds** (configurable by health system):

```python
thresholds = {
    "min_subgroup_n": 100,                    # Minimum subgroup size
    "demographic_parity_ratio": (0.8, 1.25),  # EEOC 80% rule
    "equalized_odds_diff": 0.1,               # Max TPR/FPR difference
    "calibration_diff": 0.05,                 # Max calibration error
    "min_auroc": 0.65,                        # Minimum acceptable AUROC
    "max_missing_rate": 0.10,                 # Max missing data rate
}
```

#### `AuditResults`

Results container with visualization and export capabilities.

**Attributes**:
- `config`: FairnessConfig used for the audit
- `audit_id`: Unique identifier for this audit run
- `run_timestamp`: ISO timestamp when the audit executed
- `descriptive_stats`: Cohort characteristics (Table 1)
- `overall_performance`: Discrimination, calibration & classification metrics
- `subgroup_performance`: Performance by demographic group
- `fairness_metrics`: Fairness metrics per attribute
- `intersectional`: Intersectional analysis results
- `flags`: List of metrics outside thresholds
- `governance_recommendation`: Summary statistics

**Visualization Methods**:

```python
# Executive summaries
results.plot_executive_summary()              # Single-page governance overview
results.plot_go_nogo_scorecard()              # Checklist-style scorecard
results.plot_fairness_dashboard()             # 4-panel comprehensive dashboard

# Overall performance
results.plot_discrimination()                 # ROC and PR curves
results.plot_overall_calibration()            # Calibration curve
results.plot_threshold_analysis()             # Threshold sensitivity
results.plot_decision_curve()                 # Decision curve analysis

# Subgroup analysis
results.plot_subgroup_performance(metric="auroc")  # Subgroup comparison
results.plot_calibration(by="race")           # Stratified calibration
```

**Export Methods**:

```python
# Data Scientist output (full technical)
results.to_html("report.html")
results.to_pdf("report.pdf")

# Governance output (streamlined)
results.to_html("gov.html", persona="governance")
results.to_pdf("gov.pdf", persona="governance")
results.to_governance_html("gov.html")        # Convenience method
results.to_governance_pdf("gov.pdf")          # Convenience method

# PowerPoint (always governance-focused)
results.to_pptx("deck.pptx")

# JSON for programmatic use
results.to_json("metrics.json")

# Open in browser
results.to_html("report.html", open_browser=True)
```

Reports include an **Audit Trail** section documenting the audit ID, run timestamp, model name and version, and configuration. JSON exports include the same metadata under `audit_metadata`.

### Enums

#### `OutputPersona`

```python
from faircareai.core.config import OutputPersona

OutputPersona.DATA_SCIENTIST  # Full technical output
OutputPersona.GOVERNANCE      # Streamlined 3-5 page output
```

#### `FairnessMetric`

```python
from faircareai.core.config import FairnessMetric

FairnessMetric.DEMOGRAPHIC_PARITY
FairnessMetric.EQUALIZED_ODDS
FairnessMetric.EQUAL_OPPORTUNITY
FairnessMetric.PREDICTIVE_PARITY
FairnessMetric.CALIBRATION
FairnessMetric.INDIVIDUAL_FAIRNESS
```

#### `UseCaseType`

```python
from faircareai.core.config import UseCaseType

UseCaseType.INTERVENTION_TRIGGER
UseCaseType.RISK_COMMUNICATION
UseCaseType.RESOURCE_ALLOCATION
UseCaseType.SCREENING
UseCaseType.DIAGNOSIS_SUPPORT
```

---

## Accessibility Features

Accessibility is a first-class concern in all FairCareAI output.

### WCAG 2.1 AA Compliance

All visualizations meet or exceed WCAG 2.1 Level AA standards:

- **Text Contrast**: Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text
- **Color Independence**: Information never conveyed by color alone (icons, patterns, labels used)
- **Font Size**: Minimum 14px for all text in governance reports, 12px for data scientist reports
- **Zoom Support**: Layouts remain usable at 200% zoom
- **Screen Reader Support**: Alt text provided for all figures via Plotly metadata

### Colorblind-Safe Palettes

FairCareAI uses colorblind-safe palettes tested with CVD (color vision deficiency) simulation:

- **Primary Palette**: Blue (#0072B2) and Orange (#E69F00) — Okabe-Ito, distinguishable for all CVD types
- **Status Colors**: Green (success), Yellow (warning), Red (error) - supplemented with icons
- **Subgroup Colors**: Carefully selected categorical palette avoiding red-green confusion

Tested with:
- Protanopia (red-blind)
- Deuteranopia (green-blind)
- Tritanopia (blue-blind)
- Monochromacy (grayscale)

### Publication-Ready Typography

Governance reports follow publication style guidelines:

- **Body text**: 14px (minimum)
- **Headings**: 16-20px, bold
- **Chart labels**: 14px
- **Annotations**: 14px
- **Font family**: Sans-serif (Arial, Helvetica, system default)

### Plain Language

All governance outputs use plain language principles:

- **Active voice**: "The model predicts..." not "Predictions are made..."
- **Short sentences**: <25 words average
- **Defined jargon**: Technical terms explained on first use
- **Concrete examples**: "20% of patients" not "0.2 probability"
- **Clear headings**: Descriptive section titles

---

## Governance Compliance

FairCareAI generates structured governance artifacts that cover the core criteria for responsible AI deployment in clinical settings.

| Governance Criterion | FairCareAI Feature | How FairCareAI addresses it |
|---|---|---|
| Model identification | Model identity fields | `model_name`, `model_version`, `intended_use` in config |
| Intended population | Population scope | `intended_population` field with validation |
| Data quality | Quality checks | Missing data rate flags, minimum subgroup size checks |
| Sample size adequacy | Subgroup size | Configurable `min_subgroup_n` threshold with warnings |
| Fairness metric selection | Metric recommendation | `primary_fairness_metric` with context-based recommendations |
| Fairness justification | Justification field | Required `fairness_justification` field (blocks run if missing) |
| Out-of-scope documentation | Scope limits | `out_of_scope` list in config |

### Governance Report Sections

Generated reports include 7 governance-aligned sections:

1. **Executive Summary** - Go/no-go advisory with key findings
2. **Descriptive Statistics** - Cohort characteristics (Table 1)
3. **Overall Performance** - AUROC, AUPRC, calibration, and classification metrics
4. **Subgroup Performance** - Performance by demographic group
5. **Fairness Assessment** - Disparity analysis with confidence intervals
6. **Limitations & Flags** - Warnings and considerations
7. **Governance Decision** - Sign-off section for stakeholders

### Threshold Configuration

Default thresholds are evidence-based starting points. Health systems should adjust based on context:

```python
config = FairnessConfig(
    model_name="My Model",
    thresholds={
        "min_subgroup_n": 100,                    # Adjust based on power requirements
        "demographic_parity_ratio": (0.8, 1.25),  # EEOC 80% rule
        "equalized_odds_diff": 0.1,               # Adjust based on clinical impact
        "calibration_diff": 0.05,                 # Adjust based on decision context
        "min_auroc": 0.65,                        # Adjust based on use case
        "max_missing_rate": 0.10,                 # Adjust based on data quality standards
    }
)
```

---

## CLI and Dashboard

### Command Line

```bash
faircareai --help
```

Run audits directly from the terminal:

```bash
# Audit a Parquet file (recommended for large datasets)
faircareai audit predictions.parquet -p risk_score -t outcome -o report.html

# Audit a CSV file
faircareai audit patient_data.csv -p risk_score -t readmit_30d -a race -a sex

# Specify output format explicitly
faircareai audit data.parquet -p prob -t label --format html --output fairness_report.html

# Generate governance PDF report
faircareai audit data.csv -p risk_score -t outcome --persona governance --format pdf -o governance.pdf

# Run with custom threshold
faircareai audit predictions.parquet -p risk_score -t outcome --threshold 0.3
```

**CLI Options**:
| Option | Description | Example |
|--------|-------------|---------|
| `-p`, `--pred-col` | Prediction column name | `-p risk_score` |
| `-t`, `--target-col` | Target/outcome column name | `-t readmit_30d` |
| `-a`, `--attributes` | Sensitive attribute (repeatable) | `-a race -a sex` |
| `-o`, `--output` | Output file path | `-o report.html` |
| `--format` | Output format (html, pdf, pptx, json, png, model-card, ai-model-card, ai-model-card-json, raic-checklist, repro-bundle) | `--format pdf` |
| `--persona` | Output persona (data_scientist, governance) | `--persona governance` |
| `--include-optional` | Include optional metrics in data scientist output | `--include-optional` |
| `--seed` | Random seed for bootstrap | `--seed 42` |
| `--threshold` | Decision threshold (0-1) | `--threshold 0.3` |

### Streamlit Dashboard

Launch the dashboard for upload, analysis, and export without writing code:

```python
import faircareai
faircareai.launch()
```

Or from the command line:

```bash
faircareai dashboard
```

**Dashboard Features**:
- Upload data via CSV/Parquet file
- Interactive attribute selection
- Real-time visualization updates
- Threshold adjustment sliders
- Export reports directly from UI

---

## Configuration

```python
from faircareai import FairCareAudit, FairnessConfig, FairnessMetric, UseCaseType

audit = FairCareAudit(
    data="predictions.parquet",
    pred_col="risk_score",
    target_col="readmit_30d",
    threshold=0.3,
)

# Auto-detect demographic columns or add custom ones
audit.suggest_attributes()
audit.accept_suggested_attributes([1, 2, 3])
audit.add_sensitive_attribute(
    name="language",
    column="primary_language",
    reference="English",
    clinical_justification="Language barriers affect care coordination",
)

audit.config = FairnessConfig(
    model_name="30-Day Readmission Risk Model",
    model_version="2.1.0",
    intended_use="Identify high-risk patients for care management outreach",
    intended_population="Adult inpatients discharged from medicine or surgery",
    out_of_scope=["Pediatric patients", "Psychiatric admissions"],
    primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
    fairness_justification=(
        "Model triggers a beneficial intervention. Equalized odds ensures "
        "equal TPR/FPR across groups, preventing differential access to care."
    ),
    use_case_type=UseCaseType.INTERVENTION_TRIGGER,
    organization_name="Example Health System",
    # Thresholds are evidence-based defaults; adjust for your context
    thresholds={
        "min_subgroup_n": 150,
        "equalized_odds_diff": 0.08,
        "min_auroc": 0.70,
    },
)

results = audit.run(bootstrap_ci=True, n_bootstrap=1000)
results.to_pdf("technical_validation.pdf")
results.to_governance_pdf("governance_review.pdf")
results.to_pptx("committee_presentation.pptx")
```

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and ensure:

1. **Tests pass**: `uv run pytest tests/`
2. **Code follows style**: `uv run ruff check src/` and `uv run mypy src/faircareai`
3. **Documentation updated**: Update README and docstrings for any changed behavior
4. **Scientific claims cited**: Include references for any new methodology

### Development Setup

```bash
git clone https://github.com/riccc-rush-lab/faircareai.git
cd faircareai

uv sync --extra dev
pre-commit install

# Run tests, type check, lint
uv run pytest tests/
uv run mypy src/faircareai
uv run ruff check src/
```

### Areas for Contribution

- Additional fairness metrics (individual fairness, counterfactual fairness)
- Support for multiclass classification and regression
- Integration with MLOps platforms (MLflow, Weights & Biases)
- Additional export formats (Word, LaTeX)
- Translations for internationalization

---

## Citation

If you use FairCareAI in your research or clinical implementation, please cite:

```bibtex
@software{faircareai,
  title = {FairCareAI: Healthcare AI Fairness Auditing},
  author = {FairCareAI Contributors},
  year = {2026},
  url = {https://github.com/riccc-rush-lab/faircareai},
  version = {0.2.7},
  note = {Python package for auditing ML fairness in healthcare}
}
```

---

## Funding

This project was supported by the Institute for Translational Medicine (ITM) at the University of Chicago and Rush University, funded by the National Center for Advancing Translational Sciences (NCATS) of the National Institutes of Health (NIH) through Grant Number **UL1TR002389** (Clinical and Translational Science Award). The content is solely the responsibility of the authors and does not necessarily represent the official views of the NIH.

---

## References

### Fairness Theory

- **Chouldechova, A.** (2017). Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data*, 5(2), 153-163.
- **Hardt, M., Price, E., & Srebro, N.** (2016). Equality of opportunity in supervised learning. *Advances in Neural Information Processing Systems*, 29.
- **Kleinberg, J., Mullainathan, S., & Raghavan, M.** (2017). Inherent trade-offs in the fair determination of risk scores. *Proceedings of the 8th Innovations in Theoretical Computer Science Conference*.

### Clinical ML Reporting

- **Collins, G.S., Dhiman, P., Andaur Navarro, C.L., et al.** (2024). Protocol for development of a reporting guideline (TRIPOD-AI) and risk of bias tool (PROBAST-AI) for diagnostic and prognostic prediction model studies based on artificial intelligence. *BMJ Open*, 11(7), e048008.
- **Van Calster, B., Collins, G.S., Vickers, A.J., et al.** (2025). Evaluation of performance measures in predictive artificial intelligence models to support medical decisions: overview and guidance. *The Lancet Digital Health*. https://doi.org/10.1016/j.landig.2025.100916

### Governance Frameworks

- **Coalition for Health AI (CHAI)**. (2025). Responsible AI Checkpoint 1 Checklist (official PDF). Retrieved from https://chai.org/wp-content/uploads/2025/02/Responsible-AI-Checkpoint-1-CHAI-Responsible-AI-Checklist.pdf
- **FDA.** (2021). Artificial Intelligence/Machine Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan.

### Healthcare Disparities

- **Obermeyer, Z., Powers, B., Vogeli, C., & Mullainathan, S.** (2019). Dissecting racial bias in an algorithm used to manage the health of populations. *Science*, 366(6464), 447-453.
- **Rajkomar, A., Hardt, M., Howell, M.D., Corrado, G., & Chin, M.H.** (2018). Ensuring fairness in machine learning to advance health equity. *Annals of Internal Medicine*, 169(12), 866-872.

---

## Support

- **Documentation**: See [docs/](docs/) folder for detailed guides
  - [USAGE.md](docs/USAGE.md) - Quickstart and end-to-end usage
  - [METHODOLOGY.md](docs/METHODOLOGY.md) - Scientific foundation and fairness theory
  - [PDF_SETUP_GUIDE.md](docs/PDF_SETUP_GUIDE.md) - PDF export setup
  - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and data flow
  - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- **Issues**: [GitHub Issues](https://github.com/riccc-rush-lab/faircareai/issues)
- **Community Q&A**: Use [GitHub Discussions](https://github.com/riccc-rush-lab/faircareai/discussions) for questions and feature requests
- **Code of Conduct**: See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Security**: See [SECURITY.md](SECURITY.md)

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

---

## Disclaimer

FairCareAI provides evidence-based guidance for fairness auditing. All outputs are **ADVISORY**. Final deployment decisions rest with the health system, clinical governance committees, and regulatory authorities who understand local context, patient populations, and organizational values.

This software is provided "as is" without warranty of any kind. Healthcare organizations are responsible for validating all outputs in their specific clinical context before deployment.
