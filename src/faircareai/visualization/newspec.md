# FairCareAI Package Design Document

## Governance Philosophy

> **FairCareAI provides evidence-based guidance and evidence. Final decisions rest with the data scientist and health system.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DECISION AUTHORITY MODEL                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────┐         ┌─────────────────────────────────────┐  │
│   │     FairCareAI      │         │   Data Scientist + Health System    │  │
│   │     PROVIDES:       │         │   DECIDES:                          │  │
│   ├─────────────────────┤         ├─────────────────────────────────────┤  │
│   │ • governance-aligned      │         │ • Which fairness metric to          │  │
│   │   framework         │  ───►   │   prioritize (with justification)   │  │
│   │ • Metric calculations│        │ • Acceptable thresholds             │  │
│   │ • Visualizations    │         │ • Whether to proceed to deployment  │  │
│   │ • Flags & warnings  │         │ • Mitigation strategies             │  │
│   │ • Evidence for CHAI │         │ • Risk tolerance                    │  │
│   │   checklist         │         │ • Clinical context interpretation   │  │
│   │ • Suggested actions │         │                                     │  │
│   │   (NOT mandates)    │         │ ⚠️ FINAL AUTHORITY ALWAYS HUMAN    │  │
│   └─────────────────────┘         └─────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Principles:**

1. **Package suggests, humans decide** — FairCareAI recommends fairness metrics based on use case, but the data scientist selects and justifies their choice.

2. **Thresholds are configurable** — Default thresholds (e.g., demographic parity ratio 0.8-1.25) are evidence-based starting points, not mandates. Health systems set their own based on context.

3. **Flags are informational** — Warnings highlight potential issues per CHAI criteria. They do not block deployment — that decision belongs to governance committees.

4. **"Recommendation" ≠ "Requirement"** — Output like `CONDITIONAL` or `NOT_READY` is guidance to facilitate discussion, not a verdict.

5. **Context is king** — A flag that's critical for one use case may be acceptable for another. Only humans with clinical context can make that call.

6. **CHAI framework as foundation** — All guidance traces back to CHAI RAIC criteria, giving health systems confidence they're following industry best practices while retaining autonomy.

---

## Requirements Checklist ✅

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Data scientist finds on GitHub, installs via pip | ✅ | `pip install faircareai` |
| 2 | Load CSV or Parquet file | ✅ | `FairCareAudit(data="file.parquet")` |
| 3 | User provides model_prob column | ✅ | `pred_col="model_prob"` parameter |
| 4 | User provides model_target column (readmission, death, no-show, etc.) | ✅ | `target_col="readmit_30d"` parameter |
| 5 | Support binary classifiers | ✅ | `ModelType.BINARY_CLASSIFIER` |
| 6 | Support risk scores | ✅ | `ModelType.RISK_SCORE` |
| 7 | User sets column names for their data | ✅ | All column names are user-specified |
| 8 | Package SUGGESTS sensitive attributes | ✅ | `audit.suggest_attributes()` auto-detects |
| 9 | User CHOOSES which attributes to use | ✅ | `audit.accept_suggested_attributes()` or `add_sensitive_attribute()` |
| 10 | **FORCED** fairness metric prioritization | ✅ | `config.validate()` errors if not set |
| 11 | Selection based on clinical/operational use case | ✅ | `use_case_type` + decision tree |
| 12 | Impossibility theorem acknowledgment | ✅ | `get_impossibility_warning()` |
| 13 | Visuals for governance committee | ✅ | Plotly dashboard, PDF reports |
| 14 | CHAI RAIC framework compliance | ✅ | Auto-generated evidence snippets |
| 15 | Go/no-go decision support (advisory) | ✅ | `governance_recommendation` output |
| 16 | **Descriptive stats: cohort overview** | ✅ | `descriptive_stats["cohort_overview"]` |
| 17 | **Descriptive stats: outcome rate in test data** | ✅ | Prevalence in `cohort_overview` |
| 18 | **Descriptive stats: outcome by sensitive attrs** | ✅ | `outcome_by_attribute` with rate ratios |
| 19 | **evidence-based guidance, human decisions** | ✅ | Disclaimers throughout, advisory language |
| 20 | **TRIPOD+AI: AUROC with 95% CI** | ✅ | `overall_performance["discrimination"]` |
| 21 | **TRIPOD+AI: AUPRC with 95% CI** | ✅ | `overall_performance["discrimination"]` |
| 22 | **TRIPOD+AI: Calibration (slope, intercept, plot)** | ✅ | `overall_performance["calibration"]` |
| 23 | **PPV at user-set high-risk threshold** | ✅ | `overall_performance["classification_at_threshold"]` |
| 24 | **Threshold toggle/sensitivity analysis** | ✅ | `overall_performance["threshold_analysis"]` |
| 25 | **Decision Curve Analysis (DCA)** | ✅ | `overall_performance["decision_curve"]` |
| 26 | **Confusion matrix** | ✅ | `overall_performance["confusion_matrix"]` |

---

## Gap Analysis: Existing Python Packages

| Package | Performance | Fairness | Healthcare Focus | CHAI Compliance | Governance Reports |
|---------|-------------|----------|------------------|-----------------|---------------------|
| `fairlearn` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `aif360` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `scikit-learn` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `ydata-profiling` | ✅ | ❌ | ❌ | ❌ | ❌ |
| **`faircareai`** | ✅ | ✅ | ✅ | ✅ | ✅ |

**FairCareAI fills the gap**: No existing package combines performance metrics, fairness assessment, healthcare-specific guidance, CHAI framework compliance, AND governance-ready reports.

---

## Standard Report Sections (All Reports)

Every FairCareAI report includes these sections in order:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAIRCAREAI STANDARD REPORT STRUCTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SECTION 1: DESCRIPTIVE STATISTICS (Table 1)                                │
│  ├── 1.1 Cohort Overview (total N, outcome N, prevalence)                   │
│  ├── 1.2 Sensitive Attribute Distributions (N, %, missing)                  │
│  ├── 1.3 Outcome Rates by Sensitive Attribute (rate, rate ratio, CI)        │
│  ├── 1.4 Model Prediction Distribution (mean, SD, percentiles)              │
│  └── 1.5 Prediction Distribution by Sensitive Attribute                     │
│                                                                             │
│  SECTION 2: OVERALL MODEL PERFORMANCE (TRIPOD+AI) ◄── BEFORE fairness!      │
│  ├── 2.1 Discrimination (AUROC, AUPRC with 95% CI, ROC/PR curves)           │
│  ├── 2.2 Calibration (Brier, slope, intercept, O:E ratio, plot)             │
│  ├── 2.3 Classification at Threshold (Sens, Spec, PPV, NPV, F1)             │
│  │       └── 🎚️ User-set "high risk" threshold with toggle                  │
│  ├── 2.4 Threshold Sensitivity Analysis (metrics across cutoffs)            │
│  ├── 2.5 Decision Curve Analysis (clinical utility)                         │
│  └── 2.6 Confusion Matrix                                                   │
│                                                                             │
│  SECTION 3: SUBGROUP MODEL PERFORMANCE                                      │
│  ├── 3.1 Performance by Sensitive Attribute (AUROC, calibration per group)  │
│  ├── 3.2 Subgroup Performance Heatmap                                       │
│  └── 3.3 Intersectional Analysis (if enabled)                               │
│                                                                             │
│  SECTION 4: FAIRNESS ASSESSMENT                                             │
│  ├── 4.1 Primary Fairness Metric (user-selected with justification)         │
│  ├── 4.2 Parity Metrics Dashboard                                           │
│  │   ├── Demographic Parity Ratio                                           │
│  │   ├── Equalized Odds Difference (TPR, FPR)                               │
│  │   ├── Predictive Parity Ratio                                            │
│  │   └── Calibration Difference                                             │
│  └── 4.3 Impossibility Theorem Acknowledgment                               │
│                                                                             │
│  SECTION 5: LIMITATIONS & FLAGS                                             │
│  ├── 5.1 Sample Size Limitations                                            │
│  ├── 5.2 Data Quality Flags                                                 │
│  ├── 5.3 Fairness Metric Violations                                         │
│  └── 5.4 Documented Limitations                                             │
│                                                                             │
│  SECTION 6: CHAI EVIDENCE DOCUMENTATION                                     │
│  ├── 6.1 CHAI Criteria Mapping                                              │
│  └── 6.2 Evidence Snippets for RAIC Checklist                               │
│                                                                             │
│  SECTION 7: GOVERNANCE ADVISORY (NOT MANDATE)                               │
│  ├── 7.1 Advisory Status (READY / CONDITIONAL / REVIEW_REQUIRED)            │
│  ├── 7.2 Key Considerations for Committee                                   │
│  ├── 7.3 Decision Options (checkboxes for committee)                        │
│  └── 7.4 Signature Block                                                    │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════   │
│  ⚠️  DISCLAIMER: This report provides evidence-based guidance.               │
│      Final deployment decisions rest with the data scientist and            │
│      health system governance committee.                                    │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Vision
A Python package that enables data scientists to conduct fairness/equity audits on ML models and automatically generates CHAI RAIC-compliant documentation for governance committees.

## Dual User Personas

### Data Scientist
- Wants: Quick setup, programmatic API, clear metrics, reproducible results
- Workflow: Jupyter notebook, CI/CD pipeline integration
- Output: Metrics dict, plots, exportable report

### Governance Committee
- Wants: Standardized documentation, CHAI compliance evidence, decision support
- Workflow: Review PDF/HTML reports, checklist completion
- Output: Go/no-go recommendation with documented rationale

---

## User Journey Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA SCIENTIST USER JOURNEY                          │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ 1. DISCOVER  │  GitHub search: "fairness healthcare ML"
    │    & INSTALL │  → pip install faircareai
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 2. LOAD DATA │  CSV or Parquet with:
    │              │  • model_prob (predictions)
    └──────┬───────┘  • target (readmit/death/no-show/etc.)
           │          • patient demographics
           ▼
    ┌──────────────┐
    │ 3. CONFIGURE │  User specifies:
    │   COLUMNS    │  • pred_col="model_prob"
    └──────┬───────┘  • target_col="readmit_30d"
           │
           ▼
    ┌──────────────┐
    │ 4. SENSITIVE │  Package suggests → User decides:
    │  ATTRIBUTES  │  audit.suggest_attributes()
    └──────┬───────┘  audit.accept_suggested_attributes([1,2])
           │          OR audit.add_sensitive_attribute(...)
           ▼
    ┌──────────────┐
    │ 5. FAIRNESS  │  ⚠️ FORCED STEP - Cannot skip!
    │   METRIC     │  
    │ PRIORITIZE   │  audit.suggest_fairness_metric()
    └──────┬───────┘  → Decision tree based on use case
           │          → User MUST select ONE primary metric
           │          → User MUST provide justification
           ▼
    ┌──────────────┐
    │ 6. RUN AUDIT │  results = audit.run()
    │              │  
    └──────┬───────┘  Computes:
           │          • Overall performance (AUROC, calibration)
           │          • Subgroup metrics
           │          • Fairness metrics
           │          • Flags & warnings
           ▼
    ┌──────────────┐
    │ 7. REVIEW    │  results.plot_fairness_dashboard()
    │   VISUALS    │  results.plot_calibration(by="race")
    └──────┬───────┘  results.plot_subgroup_performance()
           │
           ▼
    ┌──────────────┐
    │ 8. EXPORT    │  For GOVERNANCE COMMITTEE:
    │   REPORTS    │  results.to_html("report.html")
    └──────┬───────┘  results.to_pdf("report.pdf")
           │          results.export_chai_evidence("evidence.md")
           ▼
    ┌──────────────┐
    │ 9. GOVERNANCE│  Committee reviews:
    │   DECISION   │  • Recommendation: READY/CONDITIONAL/NOT_READY
    └──────────────┘  • CHAI checklist evidence
                      • Documented limitations
                      → GO / NO-GO DECISION
```

---

## Complete Code Example: End-to-End

```python
# Full user journey in one script

from faircareai import FairCareAudit, FairnessConfig
from faircareai.core.config import UseCaseType, FairnessMetric

# ============================================================
# STEP 1-2: Load your model predictions
# ============================================================
# Data scientist has CSV/Parquet with predictions from their model
# Columns: patient_id, model_prob, readmit_30d, race, sex, age_group, ...

audit = FairCareAudit(
    data="predictions.parquet",  # or DataFrame, or CSV path
    pred_col="model_prob",       # YOUR column name for predictions
    target_col="readmit_30d"     # YOUR column name for outcome
)

# ============================================================
# STEP 3: Package suggests sensitive attributes
# ============================================================
audit.suggest_attributes()
# Output:
# ============================================================
# SUGGESTED SENSITIVE ATTRIBUTES
# ============================================================
# FairCareAI detected the following potential sensitive attributes.
# 
# [1] RACE
#     Column: race
#     Values: ['White', 'Black', 'Hispanic', 'Asian', 'Other']
#     Missing: 2.3%
#     Suggested reference: White
# 
# [2] SEX
#     Column: sex
#     Values: ['Male', 'Female']
#     Missing: 0.1%
#     Suggested reference: Male
# ...

# ============================================================
# STEP 4: User accepts/modifies/adds attributes
# ============================================================
# Option A: Accept suggestions
audit.accept_suggested_attributes([1, 2])  # Accept race and sex

# Option B: Accept with modifications
audit.accept_suggested_attributes(
    [1], 
    modify={"race": {"reference": "Black"}}  # Change reference group
)

# Option C: Add custom attribute
audit.add_sensitive_attribute(
    name="insurance",
    column="payer_type",
    reference="Commercial",
    clinical_justification="Insurance affects care access"
)

# ============================================================
# STEP 5: FORCED - Select fairness metric with justification
# ============================================================
# First, get recommendation based on use case
rec = audit.suggest_fairness_metric()
print(rec)
# Output:
# {
#   "recommended_metric": "equalized_odds",
#   "rationale": "When model triggers an intervention...",
#   "contraindicated": ["demographic_parity"],
#   "contraindicated_reason": "..."
# }

# Create config with REQUIRED fairness prioritization
config = FairnessConfig(
    model_name="30-Day Readmission Risk",
    model_version="2.1.0",
    intended_use="Trigger care management outreach for high-risk patients",
    intended_population="Adult medicine discharges",
    out_of_scope=["Pediatrics", "Oncology", "AMA discharges"],
    
    # ⚠️ REQUIRED - Will error if not provided
    primary_fairness_metric=FairnessMetric.EQUALIZED_ODDS,
    fairness_justification="""
        Model triggers care management phone call. Equalizing TPR ensures 
        Black and Hispanic patients receive equal benefit when at risk.
        Equalizing FPR prevents disproportionate unnecessary outreach.
    """,
    use_case_type=UseCaseType.INTERVENTION_TRIGGER
)

audit.config = config

# ============================================================
# STEP 6: Run the audit
# ============================================================
results = audit.run()

print(results)
# Output:
# === FairCareAI Audit Results ===
# Model: 30-Day Readmission Risk v2.1.0
# N: 45,231
# Prevalence: 12.4%
# 
# Overall Performance:
#   AUROC: 0.742
#   AUPRC: 0.389
# 
# Governance Status: CONDITIONAL
# Flags: 2 (0 errors, 2 warnings)

# ============================================================
# STEP 7: Explore visuals
# ============================================================
# Interactive dashboard
results.plot_fairness_dashboard()

# Specific plots
results.plot_calibration(by="race")
results.plot_roc(by="race")
results.plot_subgroup_performance(metric="auroc")

# ============================================================
# STEP 8: Export for governance committee
# ============================================================
# HTML report with interactive Plotly charts
results.to_html("reports/fairness_audit_v2.1.html", open_browser=True)

# PDF for formal review
results.to_pdf("reports/fairness_audit_v2.1.pdf")

# CHAI RAIC evidence snippets for checklist
results.export_chai_evidence("reports/chai_evidence.md")

# JSON for programmatic use / CI pipeline
results.to_json("reports/metrics.json")

# ============================================================
# STEP 9: Review governance recommendation
# ============================================================
print(results.governance_recommendation)
# {
#   "status": "CONDITIONAL",
#   "advisory": "Multiple considerations identified — recommend documented mitigation plan",
#   "disclaimer": "This is evidence-based guidance. Final deployment decisions 
#                  rest with the data scientist and health system governance committee.",
#   "n_errors": 0,
#   "n_warnings": 2,
#   "warnings": [
#     {"category": "sample_size", "group": "Asian", "message": "n=87 < 100"},
#     {"category": "fairness", "metric": "equalized_odds", "group": "Hispanic", 
#      "message": "EO diff 0.12 > 0.10"}
#   ],
#   "primary_fairness_metric": "equalized_odds",
#   "justification_provided": true,
#   "chai_criteria_evaluated": ["AC1.CR1", "AC1.CR3", "AC1.CR33", ...]
# }

# The governance committee reviews and makes THEIR decision:
# - They may accept the warnings as documented limitations
# - They may require additional validation
# - They may adjust thresholds based on clinical context
# - FINAL AUTHORITY IS ALWAYS HUMAN
```

---

## Installation

```bash
pip install faircareai
```

---

## User Journey

### Step 1: Quick Start (5 lines)
```python
from faircareai import FairCareAudit

audit = FairCareAudit(
    data="predictions.parquet",
    pred_col="risk_score",
    target_col="readmit_30d"
)
audit.add_sensitive_attribute("race", reference="White")
audit.add_sensitive_attribute("sex", reference="Male")
report = audit.run()
report.to_html("fairness_report.html")
```

### Step 2: Full Configuration
```python
from faircareai import FairCareAudit, FairnessConfig

config = FairnessConfig(
    model_name="30-Day Readmission Risk Model",
    model_version="2.1.0",
    model_type="binary_classifier",  # or "risk_score"
    intended_use="Trigger care management outreach for high-risk patients",
    intended_population="Adult inpatients discharged from medicine services",
    out_of_scope=["Pediatric patients", "Oncology discharges", "AMA discharges"],
    
    # CHAI-required: Force fairness metric prioritization
    primary_fairness_metric="equalized_odds",
    fairness_justification="""
        Model triggers proactive care management intervention. 
        Equalizing TPR ensures all racial groups receive equal 
        benefit from the intervention when truly at risk.
    """,
    use_case_type="intervention_trigger",  # drives metric recommendation
    
    # Thresholds for flagging
    thresholds={
        "min_subgroup_n": 100,
        "demographic_parity_ratio": (0.8, 1.25),
        "equalized_odds_diff": 0.1,
        "calibration_diff": 0.05,
        "min_auroc": 0.65
    }
)

audit = FairCareAudit(
    data=df,  # DataFrame or path to parquet/csv
    pred_col="model_prob",
    target_col="readmit_30d",
    config=config
)

# Add sensitive attributes
audit.add_sensitive_attribute(
    name="race",
    column="patient_race",
    reference="White",
    categories=["White", "Black", "Hispanic", "Asian", "Other"],
    clinical_justification="Required for health equity monitoring per CMS guidelines"
)

audit.add_sensitive_attribute(
    name="sex", 
    column="patient_sex",
    reference="Male"
)

audit.add_sensitive_attribute(
    name="age_group",
    column="age_cat",
    categories=["18-44", "45-64", "65+"]
)

# Optional: Add intersectional analysis
audit.add_intersection(["race", "sex"])

# Run audit
results = audit.run()

# Access programmatically
print(results.overall_performance)
print(results.fairness_metrics)
print(results.flags)

# Generate reports
results.to_html("reports/fairness_report.html")
results.to_pdf("reports/fairness_report.pdf")
results.to_json("reports/fairness_metrics.json")

# Export CHAI evidence snippets
results.export_chai_evidence("reports/chai_evidence.md")
```

---

## Package Structure

```
faircareai/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── audit.py              # FairCareAudit main class
│   ├── config.py             # FairnessConfig dataclass
│   ├── results.py            # AuditResults container
│   └── validators.py         # Input validation
│
├── data/
│   ├── __init__.py
│   ├── ingest.py             # Load parquet/csv/DataFrame
│   ├── schema.py             # Data schema validation
│   └── sensitive_attrs.py    # SensitiveAttribute class
│
├── metrics/
│   ├── __init__.py
│   ├── performance.py        # AUROC, calibration, etc.
│   ├── fairness.py           # Parity metrics
│   ├── subgroup.py           # Stratified analysis
│   └── confidence.py         # Bootstrap CIs
│
├── fairness/
│   ├── __init__.py
│   ├── definitions.py        # Fairness metric definitions
│   ├── decision_tree.py      # Use case → metric mapper
│   ├── impossibility.py      # Trade-off documentation
│   └── thresholds.py         # Industry standard thresholds
│
├── visualization/
│   ├── __init__.py
│   ├── plotly_charts.py      # Interactive Plotly visuals
│   ├── altair_charts.py      # Altair alternatives
│   ├── calibration.py        # Calibration plots
│   ├── roc_curves.py         # Subgroup ROC curves
│   ├── fairness_dashboard.py # Combined fairness view
│   └── themes.py             # Consistent styling
│
├── report/
│   ├── __init__.py
│   ├── generator.py          # Main report builder
│   ├── sections/
│   │   ├── __init__.py
│   │   ├── model_identity.py
│   │   ├── data_spec.py
│   │   ├── performance.py
│   │   ├── fairness.py
│   │   ├── limitations.py
│   │   └── governance.py
│   ├── templates/
│   │   ├── report.html.j2
│   │   ├── report.pdf.j2
│   │   └── chai_evidence.md.j2
│   └── export.py             # HTML/PDF/JSON export
│
├── chai/
│   ├── __init__.py
│   ├── criteria_mapping.py   # RAIC criteria → report sections
│   ├── evidence_generator.py # Auto-generate evidence snippets
│   └── checklist.py          # Checklist status tracker
│
├── cli.py                    # Optional CLI interface
└── utils/
    ├── __init__.py
    ├── stats.py
    └── formatting.py
```

---

## Core Classes

### FairnessConfig
```python
# faircareai/core/config.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum

class ModelType(Enum):
    BINARY_CLASSIFIER = "binary_classifier"
    RISK_SCORE = "risk_score"
    MULTICLASS = "multiclass"

class UseCaseType(Enum):
    INTERVENTION_TRIGGER = "intervention_trigger"
    RISK_COMMUNICATION = "risk_communication"
    RESOURCE_ALLOCATION = "resource_allocation"
    SCREENING = "screening"
    DIAGNOSIS_SUPPORT = "diagnosis_support"

class FairnessMetric(Enum):
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    PREDICTIVE_PARITY = "predictive_parity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"

@dataclass
class FairnessConfig:
    """
    Configuration for fairness audit following CHAI RAIC framework.
    
    IMPORTANT: Default thresholds are evidence-based starting points from
    fairness literature. Health systems should adjust these based on their
    clinical context, risk tolerance, and organizational equity goals.
    
    FairCareAI provides evidence-based guidance. Final decisions on acceptable
    thresholds rest with the data scientist and health system.
    """
    
    # Model Identity (CHAI AC1.CR1-4)
    model_name: str
    model_version: str = "1.0.0"
    model_type: ModelType = ModelType.BINARY_CLASSIFIER
    
    # Intended Use (CHAI AC1.CR1, AC1.CR100)
    intended_use: str = ""
    intended_population: str = ""
    out_of_scope: List[str] = field(default_factory=list)
    
    # REQUIRED: Fairness Prioritization (CHAI AC1.CR92-93)
    # The data scientist MUST select a metric and provide justification
    # FairCareAI recommends but does not dictate the choice
    primary_fairness_metric: Optional[FairnessMetric] = None
    fairness_justification: str = ""
    use_case_type: Optional[UseCaseType] = None
    
    # Thresholds for flagging — THESE ARE CONFIGURABLE BY HEALTH SYSTEM
    # Defaults are evidence-based starting points, not requirements
    thresholds: Dict = field(default_factory=lambda: {
        "min_subgroup_n": 100,              # Adjust based on your power requirements
        "demographic_parity_ratio": (0.8, 1.25),  # 80% rule from EEOC, adjust as appropriate
        "equalized_odds_diff": 0.1,         # Adjust based on clinical impact
        "calibration_diff": 0.05,           # Adjust based on decision context
        "min_auroc": 0.65,                  # Adjust based on use case
        "max_missing_rate": 0.10            # Adjust based on data quality standards
    })
    
    # Decision threshold(s) for the model
    decision_thresholds: List[float] = field(default_factory=lambda: [0.5])
    
    # Report settings
    include_chai_mapping: bool = True
    organization_name: str = ""
    report_date: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate config and return list of warnings/errors."""
        issues = []
        
        if not self.primary_fairness_metric:
            issues.append("ERROR: primary_fairness_metric is required (CHAI AC1.CR92)")
        
        if not self.fairness_justification:
            issues.append("ERROR: fairness_justification is required (CHAI AC1.CR93)")
        
        if not self.intended_use:
            issues.append("WARNING: intended_use should be specified (CHAI AC1.CR1)")
            
        return issues
```

### Suggested Sensitive Attributes (Auto-Detection)
```python
# faircareai/data/suggested_attrs.py
"""
Suggest sensitive attributes based on common healthcare column patterns.
User can accept, modify, or ignore suggestions.
"""

from typing import List, Dict
import pandas as pd

# Common column name patterns for sensitive attributes in healthcare
SUGGESTED_PATTERNS = {
    "race": {
        "patterns": ["race", "ethnicity", "race_eth", "patient_race", "race_cd"],
        "suggested_reference": "White",
        "clinical_justification": "Required for CMS health equity monitoring and HEDIS reporting"
    },
    "sex": {
        "patterns": ["sex", "gender", "patient_sex", "sex_cd", "birth_sex"],
        "suggested_reference": "Male",
        "clinical_justification": "Biological sex may influence disease prevalence and treatment response"
    },
    "age_group": {
        "patterns": ["age_group", "age_cat", "age_bucket", "age_band"],
        "suggested_reference": None,
        "clinical_justification": "Age affects baseline risk and model generalizability"
    },
    "insurance": {
        "patterns": ["insurance", "payer", "insurance_type", "coverage", "payer_type"],
        "suggested_reference": "Commercial",
        "clinical_justification": "Insurance status correlates with access to care and outcomes"
    },
    "language": {
        "patterns": ["language", "primary_language", "lang", "language_cd"],
        "suggested_reference": "English",
        "clinical_justification": "Language barriers affect care quality and documentation completeness"
    },
    "disability": {
        "patterns": ["disability", "disabled", "disability_status"],
        "suggested_reference": "No",
        "clinical_justification": "Disability status affects care access and outcome measurement"
    }
}

def suggest_sensitive_attributes(df: pd.DataFrame) -> List[Dict]:
    """
    Scan DataFrame columns and suggest likely sensitive attributes.
    
    Returns list of suggestions that user can accept/modify/ignore.
    """
    suggestions = []
    columns_lower = {c.lower(): c for c in df.columns}
    
    for attr_name, config in SUGGESTED_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern in columns_lower:
                actual_col = columns_lower[pattern]
                unique_vals = df[actual_col].dropna().unique().tolist()
                
                suggestions.append({
                    "suggested_name": attr_name,
                    "detected_column": actual_col,
                    "unique_values": unique_vals[:10],  # First 10 for preview
                    "n_unique": len(unique_vals),
                    "missing_rate": float(df[actual_col].isna().mean()),
                    "suggested_reference": config["suggested_reference"],
                    "clinical_justification": config["clinical_justification"],
                    "accepted": False  # User must explicitly accept
                })
                break  # Only match first pattern per attribute
    
    return suggestions


def display_suggestions(suggestions: List[Dict]) -> str:
    """Format suggestions for display in notebook/CLI."""
    lines = [
        "=" * 60,
        "SUGGESTED SENSITIVE ATTRIBUTES",
        "=" * 60,
        "",
        "FairCareAI detected the following potential sensitive attributes.",
        "Review and accept/modify as appropriate for your use case.",
        ""
    ]
    
    for i, s in enumerate(suggestions, 1):
        lines.extend([
            f"[{i}] {s['suggested_name'].upper()}",
            f"    Column: {s['detected_column']}",
            f"    Values: {s['unique_values'][:5]}{'...' if len(s['unique_values']) > 5 else ''}",
            f"    Missing: {s['missing_rate']:.1%}",
            f"    Suggested reference: {s['suggested_reference']}",
            f"    Justification: {s['clinical_justification'][:60]}...",
            ""
        ])
    
    lines.extend([
        "=" * 60,
        "To accept suggestions:",
        "  audit.accept_suggested_attributes([1, 2, 3])  # by index",
        "  audit.accept_suggested_attributes(['race', 'sex'])  # by name",
        "",
        "To add custom attributes:",
        "  audit.add_sensitive_attribute(name='custom', column='my_col')",
        "=" * 60
    ])
    
    return "\n".join(lines)
```

### SensitiveAttribute
```python
# faircareai/data/sensitive_attrs.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SensitiveAttribute:
    """Defines a sensitive/protected attribute for fairness analysis."""
    
    name: str                          # Display name (e.g., "race")
    column: str                        # Column name in data
    reference: Optional[str] = None    # Reference group for comparisons
    categories: Optional[List[str]] = None  # Expected categories
    attr_type: str = "categorical"     # "categorical" or "binary"
    
    # CHAI documentation (AC1.CR48-51)
    is_protected: bool = True
    clinical_justification: Optional[str] = None
    
    def validate(self, data) -> List[str]:
        """Validate attribute against data."""
        issues = []
        
        if self.column not in data.columns:
            issues.append(f"Column '{self.column}' not found in data")
            return issues
        
        actual_values = data[self.column].dropna().unique()
        
        if self.reference and self.reference not in actual_values:
            issues.append(f"Reference '{self.reference}' not in data values")
        
        if self.categories:
            missing = set(self.categories) - set(actual_values)
            if missing:
                issues.append(f"Expected categories not found: {missing}")
        
        return issues
```

### FairCareAudit (Main Class)
```python
# faircareai/core/audit.py
import pandas as pd
from typing import Union, Optional, List
from pathlib import Path

from .config import FairnessConfig, FairnessMetric
from .results import AuditResults
from ..data.sensitive_attrs import SensitiveAttribute
from ..data.ingest import load_data
from ..metrics import performance, fairness, subgroup
from ..fairness.decision_tree import recommend_fairness_metric

class FairCareAudit:
    """
    Main class for conducting fairness audits on ML models.
    
    Follows CHAI RAIC Checkpoint 1 framework for health AI governance.
    """
    
    def __init__(
        self,
        data: Union[pd.DataFrame, str, Path],
        pred_col: str,
        target_col: str,
        config: Optional[FairnessConfig] = None,
        threshold: float = 0.5
    ):
        """
        Initialize a fairness audit.
        
        Parameters
        ----------
        data : DataFrame or path to parquet/csv
            Model predictions with outcomes and sensitive attributes
        pred_col : str
            Column name for model predictions/probabilities
        target_col : str
            Column name for actual outcomes (0/1)
        config : FairnessConfig, optional
            Full configuration object
        threshold : float
            Decision threshold for binary classification
        """
        self.data = load_data(data)
        self.pred_col = pred_col
        self.target_col = target_col
        self.threshold = threshold
        self.config = config or FairnessConfig(model_name="Unnamed Model")
        
        self.sensitive_attributes: List[SensitiveAttribute] = []
        self.intersections: List[List[str]] = []
        
        self._validate_data()
        
        # Auto-detect suggested attributes
        from ..data.suggested_attrs import suggest_sensitive_attributes
        self._suggestions = suggest_sensitive_attributes(self.data)
    
    def suggest_attributes(self, display: bool = True) -> List[dict]:
        """
        Show suggested sensitive attributes based on detected columns.
        
        Returns list of suggestions. User must explicitly accept.
        """
        if display:
            from ..data.suggested_attrs import display_suggestions
            print(display_suggestions(self._suggestions))
        return self._suggestions
    
    def accept_suggested_attributes(
        self, 
        selections: List[Union[int, str]],
        modify: Optional[Dict] = None
    ) -> "FairCareAudit":
        """
        Accept suggested sensitive attributes.
        
        Parameters
        ----------
        selections : list of int or str
            Indices (1-based) or names of suggestions to accept
        modify : dict, optional
            Overrides for accepted suggestions, e.g. {"race": {"reference": "Black"}}
        
        Returns
        -------
        self : for method chaining
        """
        modify = modify or {}
        
        for sel in selections:
            # Find the suggestion
            if isinstance(sel, int):
                if 1 <= sel <= len(self._suggestions):
                    suggestion = self._suggestions[sel - 1]
                else:
                    raise ValueError(f"Invalid index: {sel}")
            else:
                matches = [s for s in self._suggestions if s["suggested_name"] == sel]
                if not matches:
                    raise ValueError(f"No suggestion named: {sel}")
                suggestion = matches[0]
            
            # Apply any modifications
            overrides = modify.get(suggestion["suggested_name"], {})
            
            self.add_sensitive_attribute(
                name=suggestion["suggested_name"],
                column=overrides.get("column", suggestion["detected_column"]),
                reference=overrides.get("reference", suggestion["suggested_reference"]),
                categories=overrides.get("categories"),
                clinical_justification=overrides.get(
                    "clinical_justification", 
                    suggestion["clinical_justification"]
                )
            )
            
            suggestion["accepted"] = True
        
        return self
    
    def _validate_data(self):
        """Validate required columns exist."""
        required = [self.pred_col, self.target_col]
        missing = [c for c in required if c not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Validate predictions are probabilities
        pred_range = (self.data[self.pred_col].min(), self.data[self.pred_col].max())
        if pred_range[0] < 0 or pred_range[1] > 1:
            raise ValueError(f"Predictions should be probabilities [0,1], got range {pred_range}")
    
    def add_sensitive_attribute(
        self,
        name: str,
        column: Optional[str] = None,
        reference: Optional[str] = None,
        categories: Optional[List[str]] = None,
        clinical_justification: Optional[str] = None
    ) -> "FairCareAudit":
        """
        Add a sensitive attribute for fairness analysis.
        
        Parameters
        ----------
        name : str
            Display name for the attribute
        column : str, optional
            Column name in data (defaults to name)
        reference : str, optional
            Reference group for disparity calculations
        categories : list, optional
            Expected category values
        clinical_justification : str, optional
            CHAI-required justification if attribute influences model
            
        Returns
        -------
        self : for method chaining
        """
        attr = SensitiveAttribute(
            name=name,
            column=column or name,
            reference=reference,
            categories=categories,
            clinical_justification=clinical_justification
        )
        
        issues = attr.validate(self.data)
        if issues:
            raise ValueError(f"Attribute validation failed: {issues}")
        
        self.sensitive_attributes.append(attr)
        return self
    
    def add_intersection(self, attributes: List[str]) -> "FairCareAudit":
        """Add intersectional analysis (e.g., race × sex)."""
        # Validate attributes exist
        attr_names = [a.name for a in self.sensitive_attributes]
        missing = [a for a in attributes if a not in attr_names]
        if missing:
            raise ValueError(f"Attributes not registered: {missing}")
        
        self.intersections.append(attributes)
        return self
    
    def suggest_fairness_metric(self) -> dict:
        """
        Suggest appropriate fairness metric based on use case.
        
        Returns decision tree logic and recommendation.
        """
        return recommend_fairness_metric(self.config.use_case_type)
    
    def run(self, bootstrap_ci: bool = True, n_bootstrap: int = 1000) -> AuditResults:
        """
        Execute the fairness audit.
        
        Parameters
        ----------
        bootstrap_ci : bool
            Calculate bootstrap confidence intervals
        n_bootstrap : int
            Number of bootstrap iterations
            
        Returns
        -------
        AuditResults : Container with all metrics and report generation
        """
        # Validate config
        config_issues = self.config.validate()
        errors = [i for i in config_issues if i.startswith("ERROR")]
        if errors:
            raise ValueError(f"Configuration errors: {errors}")
        
        if not self.sensitive_attributes:
            raise ValueError("At least one sensitive attribute required")
        
        results = AuditResults(config=self.config)
        
        # =====================================================================
        # SECTION 1: DESCRIPTIVE STATISTICS (Table 1)
        # This is FIRST because it provides essential context for all that follows
        # =====================================================================
        from ..metrics.descriptive import compute_cohort_summary
        
        sensitive_attrs_dict = [
            {"name": a.name, "column": a.column, "reference": a.reference}
            for a in self.sensitive_attributes
        ]
        
        results.descriptive_stats = compute_cohort_summary(
            data=self.data,
            target_col=self.target_col,
            pred_col=self.pred_col,
            sensitive_attrs=sensitive_attrs_dict
        )
        
        # Also populate data_summary for backward compatibility
        results.data_summary = self._compute_data_summary()
        
        # =====================================================================
        # SECTION 2: OVERALL MODEL PERFORMANCE
        # =====================================================================
        results.overall_performance = performance.compute_overall(
            y_true=self.data[self.target_col],
            y_prob=self.data[self.pred_col],
            threshold=self.threshold,
            bootstrap_ci=bootstrap_ci,
            n_bootstrap=n_bootstrap
        )
        
        # =====================================================================
        # SECTION 3: SUBGROUP PERFORMANCE
        # =====================================================================
        results.subgroup_performance = {}
        for attr in self.sensitive_attributes:
            results.subgroup_performance[attr.name] = subgroup.compute_subgroup_metrics(
                data=self.data,
                pred_col=self.pred_col,
                target_col=self.target_col,
                group_col=attr.column,
                threshold=self.threshold,
                reference=attr.reference,
                bootstrap_ci=bootstrap_ci
            )
        
        # =====================================================================
        # SECTION 4: FAIRNESS METRICS
        # =====================================================================
        results.fairness_metrics = {}
        for attr in self.sensitive_attributes:
            results.fairness_metrics[attr.name] = fairness.compute_fairness_metrics(
                data=self.data,
                pred_col=self.pred_col,
                target_col=self.target_col,
                group_col=attr.column,
                threshold=self.threshold,
                reference=attr.reference
            )
        
        # =====================================================================
        # SECTION 5: INTERSECTIONAL ANALYSIS
        # =====================================================================
        results.intersectional = {}
        for intersection in self.intersections:
            key = " × ".join(intersection)
            cols = [self._get_attr_column(a) for a in intersection]
            results.intersectional[key] = subgroup.compute_intersectional(
                data=self.data,
                pred_col=self.pred_col,
                target_col=self.target_col,
                group_cols=cols,
                threshold=self.threshold,
                min_n=self.config.thresholds.get("min_subgroup_n", 100)
            )
        
        # 6. Generate Flags
        results.flags = self._generate_flags(results)
        
        # 7. CHAI Evidence Mapping
        results.chai_evidence = self._generate_chai_evidence(results)
        
        # 8. Governance Recommendation
        results.governance_recommendation = self._generate_recommendation(results)
        
        # Store reference to audit for visualization
        results._audit = self
        
        return results
    
    def _compute_data_summary(self) -> dict:
        """Compute data summary statistics."""
        summary = {
            "n_total": len(self.data),
            "n_positive": int(self.data[self.target_col].sum()),
            "n_negative": int((1 - self.data[self.target_col]).sum()),
            "prevalence": float(self.data[self.target_col].mean()),
            "prediction_mean": float(self.data[self.pred_col].mean()),
            "prediction_std": float(self.data[self.pred_col].std()),
            "attributes": {}
        }
        
        for attr in self.sensitive_attributes:
            col = attr.column
            summary["attributes"][attr.name] = {
                "n_groups": self.data[col].nunique(),
                "missing_rate": float(self.data[col].isna().mean()),
                "distribution": self.data[col].value_counts(normalize=True).to_dict()
            }
        
        return summary
    
    def _get_attr_column(self, name: str) -> str:
        """Get column name for attribute."""
        for attr in self.sensitive_attributes:
            if attr.name == name:
                return attr.column
        raise ValueError(f"Attribute not found: {name}")
    
    def _generate_flags(self, results: AuditResults) -> List[dict]:
        """Generate warning/error flags based on thresholds."""
        flags = []
        thresholds = self.config.thresholds
        
        # Check subgroup sample sizes
        for attr_name, subgroup_data in results.subgroup_performance.items():
            for group, metrics in subgroup_data.items():
                if metrics["n"] < thresholds.get("min_subgroup_n", 100):
                    flags.append({
                        "level": "warning",
                        "category": "sample_size",
                        "attribute": attr_name,
                        "group": group,
                        "message": f"Subgroup n={metrics['n']} < {thresholds['min_subgroup_n']}",
                        "chai_criteria": "AC1.CR82"
                    })
        
        # Check fairness metric violations
        for attr_name, fairness_data in results.fairness_metrics.items():
            # Demographic parity
            dp_range = thresholds.get("demographic_parity_ratio", (0.8, 1.25))
            if "demographic_parity_ratio" in fairness_data:
                for group, ratio in fairness_data["demographic_parity_ratio"].items():
                    if ratio < dp_range[0] or ratio > dp_range[1]:
                        flags.append({
                            "level": "warning",
                            "category": "fairness",
                            "metric": "demographic_parity",
                            "attribute": attr_name,
                            "group": group,
                            "value": ratio,
                            "threshold": dp_range,
                            "message": f"Demographic parity ratio {ratio:.2f} outside [{dp_range[0]}, {dp_range[1]}]",
                            "chai_criteria": "AC1.CR92"
                        })
            
            # Equalized odds
            eo_threshold = thresholds.get("equalized_odds_diff", 0.1)
            if "equalized_odds_diff" in fairness_data:
                for group, diff in fairness_data["equalized_odds_diff"].items():
                    if abs(diff) > eo_threshold:
                        flags.append({
                            "level": "warning",
                            "category": "fairness",
                            "metric": "equalized_odds",
                            "attribute": attr_name,
                            "group": group,
                            "value": diff,
                            "threshold": eo_threshold,
                            "message": f"Equalized odds difference {diff:.3f} > {eo_threshold}",
                            "chai_criteria": "AC1.CR92"
                        })
        
        # Check missing data rates
        for attr_name, attr_summary in results.data_summary["attributes"].items():
            max_missing = thresholds.get("max_missing_rate", 0.10)
            if attr_summary["missing_rate"] > max_missing:
                flags.append({
                    "level": "warning",
                    "category": "data_quality",
                    "attribute": attr_name,
                    "value": attr_summary["missing_rate"],
                    "threshold": max_missing,
                    "message": f"Missing rate {attr_summary['missing_rate']:.1%} > {max_missing:.0%}",
                    "chai_criteria": "AC1.CR68"
                })
        
        return flags
    
    def _generate_chai_evidence(self, results: AuditResults) -> dict:
        """Generate CHAI RAIC evidence documentation."""
        # Import here to avoid circular dependency
        from ..chai.evidence_generator import generate_evidence
        return generate_evidence(self.config, results, self.sensitive_attributes)
    
    def _generate_recommendation(self, results: AuditResults) -> dict:
        """
        Generate ADVISORY governance recommendation.
        
        NOTE: This is GUIDANCE based on CHAI criteria, not a mandate.
        Final deployment decisions rest with the health system.
        """
        errors = [f for f in results.flags if f["level"] == "error"]
        warnings = [f for f in results.flags if f["level"] == "warning"]
        
        # Advisory status based on CHAI best practices
        if errors:
            status = "REVIEW_REQUIRED"
            advisory = "Critical issues identified — recommend addressing before deployment"
        elif len(warnings) > 3:
            status = "CONDITIONAL"
            advisory = "Multiple considerations identified — recommend documented mitigation plan"
        elif warnings:
            status = "CONDITIONAL"
            advisory = "Minor considerations identified — recommend documentation"
        else:
            status = "READY"
            advisory = "No significant issues identified per CHAI criteria"
        
        return {
            "status": status,
            "advisory": advisory,  # Changed from "recommendation" to "advisory"
            "disclaimer": "This is evidence-based guidance. Final deployment decisions "
                         "rest with the data scientist and health system governance committee.",
            "n_errors": len(errors),
            "n_warnings": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "primary_fairness_metric": self.config.primary_fairness_metric.value if self.config.primary_fairness_metric else None,
            "justification_provided": bool(self.config.fairness_justification),
            "chai_criteria_evaluated": list(results.chai_evidence.keys())
        }
```

### AuditResults
```python
# faircareai/core/results.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

@dataclass
class AuditResults:
    """Container for fairness audit results with export capabilities."""
    
    config: Any  # FairnessConfig
    
    # Results - IN ORDER OF REPORT SECTIONS
    # Section 1: Descriptive Statistics (Table 1)
    descriptive_stats: Dict = field(default_factory=dict)  # NEW: cohort/outcome summary
    data_summary: Dict = field(default_factory=dict)
    
    # Section 2: Overall Model Performance
    overall_performance: Dict = field(default_factory=dict)
    
    # Section 3: Subgroup Performance
    subgroup_performance: Dict = field(default_factory=dict)
    
    # Section 4: Fairness Metrics
    fairness_metrics: Dict = field(default_factory=dict)
    intersectional: Dict = field(default_factory=dict)
    
    # Section 5: Flags & Advisory
    flags: List[Dict] = field(default_factory=list)
    chai_evidence: Dict = field(default_factory=dict)
    governance_recommendation: Dict = field(default_factory=dict)
    
    # Internal reference
    _audit: Any = None
    
    def summary(self) -> str:
        """Print summary to console."""
        desc = self.descriptive_stats
        cohort = desc.get("cohort_overview", {})
        perf = self.overall_performance
        disc = perf.get("discrimination", {})
        cal = perf.get("calibration", {})
        cls = perf.get("classification_at_threshold", {})
        
        lines = [
            f"{'='*70}",
            f"FairCareAI Audit Results",
            f"{'='*70}",
            f"Model: {self.config.model_name} v{self.config.model_version}",
            f"",
            f"SECTION 1: COHORT SUMMARY",
            f"  N:              {cohort.get('n_total', 'N/A'):,}",
            f"  Outcome:        {cohort.get('n_positive', 'N/A'):,} ({cohort.get('prevalence_pct', 'N/A')})",
            f"",
            f"SECTION 2: OVERALL MODEL PERFORMANCE (TRIPOD+AI)",
            f"  Discrimination:",
            f"    AUROC:        {disc.get('auroc', 'N/A'):.3f} {disc.get('auroc_ci_fmt', '')}",
            f"    AUPRC:        {disc.get('auprc', 'N/A'):.3f} {disc.get('auprc_ci_fmt', '')}",
            f"  Calibration:",
            f"    Brier Score:  {cal.get('brier_score', 'N/A'):.4f}",
            f"    Cal. Slope:   {cal.get('calibration_slope', 'N/A'):.2f} (ideal: 1.00)",
            f"  At Threshold = {cls.get('threshold', 'N/A')}:",
            f"    Sensitivity:  {cls.get('sensitivity', 0):.1%}",
            f"    Specificity:  {cls.get('specificity', 0):.1%}",
            f"    PPV:          {cls.get('ppv', 0):.1%}",
            f"    % Flagged:    {cls.get('pct_flagged', 0):.1f}%",
            f"",
            f"SECTION 4: FAIRNESS SUMMARY",
            f"  Primary metric: {self.config.primary_fairness_metric.value if self.config.primary_fairness_metric else 'Not set'}",
            f"",
            f"SECTION 7: ADVISORY STATUS: {self.governance_recommendation.get('status', 'N/A')}",
            f"  {self.governance_recommendation.get('advisory', '')}",
            f"  Flags: {len(self.flags)} ({self.governance_recommendation.get('n_errors', 0)} critical, {self.governance_recommendation.get('n_warnings', 0)} warnings)",
            f"",
            f"{'='*70}",
            f"⚠️  This is evidence-based guidance. Final decisions rest with",
            f"    the data scientist and health system governance committee.",
            f"{'='*70}",
        ]
        return "\n".join(lines)
    
    def print_table1(self) -> str:
        """Print Table 1 descriptive statistics."""
        from ..metrics.descriptive import format_table1_text
        text = format_table1_text(self.descriptive_stats)
        print(text)
        return text
    
    def get_table1_dataframe(self) -> "pd.DataFrame":
        """Get Table 1 as a pandas DataFrame for export."""
        from ..metrics.descriptive import generate_table1_dataframe
        return generate_table1_dataframe(self.descriptive_stats)
    
    def __repr__(self):
        return self.summary()
    
    # === Export Methods ===
    
    def to_html(self, path: str, open_browser: bool = False):
        """Export interactive HTML report."""
        from ..report.generator import generate_html_report
        generate_html_report(self, path)
        if open_browser:
            import webbrowser
            webbrowser.open(Path(path).absolute().as_uri())
    
    def to_pdf(self, path: str):
        """Export PDF report for governance review."""
        from ..report.generator import generate_pdf_report
        generate_pdf_report(self, path)
    
    def to_json(self, path: str):
        """Export metrics as JSON for programmatic use."""
        import json
        export_data = {
            "config": {
                "model_name": self.config.model_name,
                "model_version": self.config.model_version,
                "primary_fairness_metric": self.config.primary_fairness_metric.value if self.config.primary_fairness_metric else None,
                "fairness_justification": self.config.fairness_justification
            },
            "data_summary": self.data_summary,
            "overall_performance": self.overall_performance,
            "subgroup_performance": self.subgroup_performance,
            "fairness_metrics": self.fairness_metrics,
            "flags": self.flags,
            "governance_recommendation": self.governance_recommendation
        }
        with open(path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def export_chai_evidence(self, path: str):
        """Export CHAI RAIC evidence snippets for checklist."""
        from ..chai.evidence_generator import export_evidence_markdown
        export_evidence_markdown(self.chai_evidence, path)
    
    # === Visualization Methods ===
    
    # --- Section 2: Overall Performance Plots ---
    
    def plot_discrimination(self, engine: str = "plotly"):
        """Plot ROC and Precision-Recall curves (TRIPOD+AI 2.1)."""
        from ..visualization.performance_charts import plot_discrimination_curves
        return plot_discrimination_curves(self)
    
    def plot_overall_calibration(self, engine: str = "plotly"):
        """Plot calibration curve for overall model (TRIPOD+AI 2.2)."""
        from ..visualization.performance_charts import plot_calibration
        return plot_calibration(self)
    
    def plot_threshold_analysis(self, selected_threshold: float = None, engine: str = "plotly"):
        """
        Interactive threshold sensitivity analysis (TRIPOD+AI 2.4).
        
        Data scientist can TOGGLE threshold to see metric impacts.
        """
        from ..visualization.performance_charts import plot_threshold_analysis
        thresh = selected_threshold or self.overall_performance.get("primary_threshold", 0.5)
        return plot_threshold_analysis(self, selected_threshold=thresh)
    
    def plot_decision_curve(self, engine: str = "plotly"):
        """Plot Decision Curve Analysis for clinical utility (TRIPOD+AI 2.5)."""
        from ..visualization.performance_charts import plot_decision_curve
        return plot_decision_curve(self)
    
    def plot_performance_summary(self, engine: str = "plotly"):
        """Plot all Section 2 performance visualizations in one dashboard."""
        from ..visualization.performance_charts import (
            plot_discrimination_curves, plot_calibration,
            plot_threshold_analysis, plot_decision_curve
        )
        from plotly.subplots import make_subplots
        # Implementation would combine all plots into single figure
        pass
    
    # --- Section 3: Subgroup Performance Plots ---
    
    def plot_calibration(self, by: Optional[str] = None, engine: str = "plotly"):
        """
        Plot calibration curve(s).
        
        Parameters
        ----------
        by : str, optional
            Sensitive attribute to stratify by
        engine : str
            "plotly" or "altair"
        """
        from ..visualization import calibration
        if engine == "plotly":
            return calibration.plot_calibration_plotly(self, by=by)
        else:
            return calibration.plot_calibration_altair(self, by=by)
    
    def plot_roc(self, by: Optional[str] = None, engine: str = "plotly"):
        """Plot ROC curve(s) by subgroup."""
        from ..visualization import roc_curves
        if engine == "plotly":
            return roc_curves.plot_roc_plotly(self, by=by)
        else:
            return roc_curves.plot_roc_altair(self, by=by)
    
    def plot_fairness_dashboard(self, engine: str = "plotly"):
        """Plot comprehensive fairness dashboard."""
        from ..visualization import fairness_dashboard
        if engine == "plotly":
            return fairness_dashboard.plot_dashboard_plotly(self)
        else:
            return fairness_dashboard.plot_dashboard_altair(self)
    
    def plot_subgroup_performance(self, metric: str = "auroc", engine: str = "plotly"):
        """Plot subgroup performance comparison."""
        from ..visualization import subgroup_charts
        if engine == "plotly":
            return subgroup_charts.plot_subgroup_plotly(self, metric=metric)
        else:
            return subgroup_charts.plot_subgroup_altair(self, metric=metric)
```

---

## Fairness Metrics Module

### Descriptive Statistics Module (Table 1 for ML)

```python
# faircareai/metrics/descriptive.py
"""
Descriptive statistics for cohort, outcomes, and model performance.
This "Table 1" equivalent is REQUIRED for all reports — provides essential
context before fairness analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats

def compute_cohort_summary(
    data: pd.DataFrame,
    target_col: str,
    pred_col: str,
    sensitive_attrs: List[dict]
) -> Dict:
    """
    Compute comprehensive cohort descriptive statistics.
    
    This is the foundation for all reports — shows WHO is in the data,
    WHAT the outcome rates are, and HOW the model performs overall.
    
    Returns
    -------
    dict with:
        - cohort_overview: total N, outcome rates
        - outcome_by_attribute: outcome rates stratified by sensitive attributes
        - prediction_distribution: model score distribution
        - model_performance_overall: AUROC, AUPRC, calibration for full cohort
    """
    results = {}
    
    # =========================================================================
    # SECTION 1: COHORT OVERVIEW
    # =========================================================================
    n_total = len(data)
    n_positive = int(data[target_col].sum())
    n_negative = n_total - n_positive
    prevalence = data[target_col].mean()
    
    results["cohort_overview"] = {
        "n_total": n_total,
        "n_positive": n_positive,
        "n_negative": n_negative,
        "prevalence": prevalence,
        "prevalence_pct": f"{prevalence:.1%}",
        "outcome_label": target_col
    }
    
    # =========================================================================
    # SECTION 2: SENSITIVE ATTRIBUTE DISTRIBUTIONS
    # =========================================================================
    results["attribute_distributions"] = {}
    
    for attr in sensitive_attrs:
        col = attr["column"]
        name = attr["name"]
        
        # Value counts
        value_counts = data[col].value_counts(dropna=False)
        value_pcts = data[col].value_counts(normalize=True, dropna=False)
        
        # Missing data
        n_missing = data[col].isna().sum()
        pct_missing = data[col].isna().mean()
        
        results["attribute_distributions"][name] = {
            "column": col,
            "n_unique": data[col].nunique(),
            "n_missing": n_missing,
            "pct_missing": pct_missing,
            "pct_missing_fmt": f"{pct_missing:.1%}",
            "distribution": {
                str(k): {"n": int(v), "pct": f"{value_pcts.get(k, 0):.1%}"}
                for k, v in value_counts.items()
            }
        }
    
    # =========================================================================
    # SECTION 3: OUTCOME RATES BY SENSITIVE ATTRIBUTE (Descriptive)
    # =========================================================================
    results["outcome_by_attribute"] = {}
    
    for attr in sensitive_attrs:
        col = attr["column"]
        name = attr["name"]
        reference = attr.get("reference")
        
        outcome_rates = {}
        groups = data[col].dropna().unique()
        
        for group in groups:
            mask = data[col] == group
            group_data = data[mask]
            n_group = len(group_data)
            n_positive_group = int(group_data[target_col].sum())
            rate = group_data[target_col].mean()
            
            outcome_rates[str(group)] = {
                "n": n_group,
                "n_positive": n_positive_group,
                "outcome_rate": rate,
                "outcome_rate_pct": f"{rate:.1%}",
                "is_reference": (str(group) == str(reference))
            }
        
        # Calculate rate ratios relative to reference
        if reference and str(reference) in outcome_rates:
            ref_rate = outcome_rates[str(reference)]["outcome_rate"]
            for group, stats in outcome_rates.items():
                if ref_rate > 0:
                    stats["rate_ratio_vs_ref"] = stats["outcome_rate"] / ref_rate
                    stats["rate_diff_vs_ref"] = stats["outcome_rate"] - ref_rate
        
        results["outcome_by_attribute"][name] = {
            "reference_group": reference,
            "groups": outcome_rates
        }
    
    # =========================================================================
    # SECTION 4: PREDICTION SCORE DISTRIBUTION
    # =========================================================================
    pred_values = data[pred_col].dropna()
    
    results["prediction_distribution"] = {
        "mean": float(pred_values.mean()),
        "std": float(pred_values.std()),
        "median": float(pred_values.median()),
        "min": float(pred_values.min()),
        "max": float(pred_values.max()),
        "percentiles": {
            "p5": float(pred_values.quantile(0.05)),
            "p25": float(pred_values.quantile(0.25)),
            "p50": float(pred_values.quantile(0.50)),
            "p75": float(pred_values.quantile(0.75)),
            "p95": float(pred_values.quantile(0.95))
        },
        "n_missing": int(data[pred_col].isna().sum())
    }
    
    # Score distribution by outcome
    results["prediction_by_outcome"] = {
        "positive": {
            "mean": float(data.loc[data[target_col] == 1, pred_col].mean()),
            "std": float(data.loc[data[target_col] == 1, pred_col].std()),
            "median": float(data.loc[data[target_col] == 1, pred_col].median())
        },
        "negative": {
            "mean": float(data.loc[data[target_col] == 0, pred_col].mean()),
            "std": float(data.loc[data[target_col] == 0, pred_col].std()),
            "median": float(data.loc[data[target_col] == 0, pred_col].median())
        }
    }
    
    # =========================================================================
    # SECTION 5: PREDICTION DISTRIBUTION BY SENSITIVE ATTRIBUTE
    # =========================================================================
    results["prediction_by_attribute"] = {}
    
    for attr in sensitive_attrs:
        col = attr["column"]
        name = attr["name"]
        
        pred_by_group = {}
        for group in data[col].dropna().unique():
            mask = data[col] == group
            group_preds = data.loc[mask, pred_col]
            
            pred_by_group[str(group)] = {
                "n": int(mask.sum()),
                "mean": float(group_preds.mean()),
                "std": float(group_preds.std()),
                "median": float(group_preds.median())
            }
        
        results["prediction_by_attribute"][name] = pred_by_group
    
    return results


def format_table1_text(summary: Dict) -> str:
    """Format descriptive statistics as text table for display."""
    lines = [
        "=" * 70,
        "COHORT DESCRIPTIVE STATISTICS",
        "=" * 70,
        "",
        "OVERALL COHORT",
        "-" * 40,
        f"  Total N:           {summary['cohort_overview']['n_total']:,}",
        f"  Outcome positive:  {summary['cohort_overview']['n_positive']:,} ({summary['cohort_overview']['prevalence_pct']})",
        f"  Outcome negative:  {summary['cohort_overview']['n_negative']:,}",
        ""
    ]
    
    # Attribute distributions
    lines.extend([
        "SENSITIVE ATTRIBUTE DISTRIBUTIONS",
        "-" * 40
    ])
    
    for attr_name, attr_data in summary["attribute_distributions"].items():
        lines.append(f"\n  {attr_name.upper()} (missing: {attr_data['pct_missing_fmt']})")
        for value, counts in attr_data["distribution"].items():
            lines.append(f"    {value}: n={counts['n']:,} ({counts['pct']})")
    
    # Outcome rates by attribute
    lines.extend([
        "",
        "OUTCOME RATES BY SENSITIVE ATTRIBUTE",
        "-" * 40
    ])
    
    for attr_name, attr_data in summary["outcome_by_attribute"].items():
        lines.append(f"\n  {attr_name.upper()} (reference: {attr_data['reference_group']})")
        for group, stats in attr_data["groups"].items():
            ref_marker = " [REF]" if stats.get("is_reference") else ""
            rate_ratio = f" (RR: {stats.get('rate_ratio_vs_ref', 'N/A'):.2f})" if "rate_ratio_vs_ref" in stats and not stats.get("is_reference") else ""
            lines.append(f"    {group}: {stats['outcome_rate_pct']} (n={stats['n']:,}){ref_marker}{rate_ratio}")
    
    # Prediction distribution
    lines.extend([
        "",
        "MODEL PREDICTION DISTRIBUTION",
        "-" * 40,
        f"  Mean (SD):  {summary['prediction_distribution']['mean']:.3f} ({summary['prediction_distribution']['std']:.3f})",
        f"  Median:     {summary['prediction_distribution']['median']:.3f}",
        f"  Range:      [{summary['prediction_distribution']['min']:.3f}, {summary['prediction_distribution']['max']:.3f}]",
        f"  IQR:        [{summary['prediction_distribution']['percentiles']['p25']:.3f}, {summary['prediction_distribution']['percentiles']['p75']:.3f}]",
        "",
        "  By outcome:",
        f"    Positive: mean={summary['prediction_by_outcome']['positive']['mean']:.3f} (SD={summary['prediction_by_outcome']['positive']['std']:.3f})",
        f"    Negative: mean={summary['prediction_by_outcome']['negative']['mean']:.3f} (SD={summary['prediction_by_outcome']['negative']['std']:.3f})",
        "",
        "=" * 70
    ])
    
    return "\n".join(lines)


def generate_table1_dataframe(summary: Dict) -> pd.DataFrame:
    """
    Generate a formatted Table 1 DataFrame for export/display.
    
    Standard clinical research format with N (%) for categorical variables.
    """
    rows = []
    
    # Overall
    rows.append({
        "Variable": "Total N",
        "Overall": f"{summary['cohort_overview']['n_total']:,}",
        "Category": ""
    })
    rows.append({
        "Variable": "Outcome positive",
        "Overall": f"{summary['cohort_overview']['n_positive']:,} ({summary['cohort_overview']['prevalence_pct']})",
        "Category": ""
    })
    
    # By attribute
    for attr_name, attr_data in summary["attribute_distributions"].items():
        rows.append({
            "Variable": attr_name,
            "Overall": "",
            "Category": ""
        })
        for value, counts in attr_data["distribution"].items():
            rows.append({
                "Variable": "",
                "Overall": f"{counts['n']:,} ({counts['pct']})",
                "Category": str(value)
            })
    
    return pd.DataFrame(rows)


def compute_outcome_rate_statistics(
    data: pd.DataFrame,
    target_col: str,
    group_col: str,
    reference: Optional[str] = None
) -> Dict:
    """
    Compute statistical tests for outcome rate differences between groups.
    
    Returns chi-square test and pairwise comparisons.
    """
    # Overall chi-square test
    contingency = pd.crosstab(data[group_col], data[target_col])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    results = {
        "chi_square": {
            "statistic": chi2,
            "p_value": p_value,
            "dof": dof,
            "significant_at_05": p_value < 0.05
        },
        "pairwise_comparisons": {}
    }
    
    # Pairwise comparisons vs reference
    if reference:
        ref_data = data[data[group_col] == reference]
        ref_positive = ref_data[target_col].sum()
        ref_n = len(ref_data)
        
        for group in data[group_col].dropna().unique():
            if str(group) == str(reference):
                continue
            
            group_data = data[data[group_col] == group]
            group_positive = group_data[target_col].sum()
            group_n = len(group_data)
            
            # 2x2 chi-square
            table = [[group_positive, group_n - group_positive],
                     [ref_positive, ref_n - ref_positive]]
            chi2_pair, p_pair = stats.chi2_contingency(table)[:2]
            
            results["pairwise_comparisons"][str(group)] = {
                "vs_reference": reference,
                "chi_square": chi2_pair,
                "p_value": p_pair,
                "significant_at_05": p_pair < 0.05
            }
    
    return results
```

### Report Section: Descriptive Statistics (Table 1)

Every FairCareAI report will include this section FIRST, before any model performance or fairness metrics:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECTION 1: COHORT DESCRIPTIVE STATISTICS                 │
│                    (Required for all FairCareAI reports)                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1.1 COHORT OVERVIEW                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Total Patients:        45,231                                             │
│   Outcome (Readmit 30d): 5,608 (12.4%)                                      │
│   No Outcome:            39,623 (87.6%)                                     │
│                                                                             │
│   Test Dataset Period:   Jan 2023 - Dec 2023                                │
│   Source:                Rush University Medical Center                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1.2 SENSITIVE ATTRIBUTE DISTRIBUTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RACE (2.3% missing)                                                       │
│   ├── White:      24,102 (53.3%)                                            │
│   ├── Black:      12,445 (27.5%)                                            │
│   ├── Hispanic:    5,874 (13.0%)                                            │
│   ├── Asian:       1,856 (4.1%)                                             │
│   └── Other:         954 (2.1%)                                             │
│                                                                             │
│   SEX (0.1% missing)                                                        │
│   ├── Male:       21,543 (47.6%)                                            │
│   └── Female:     23,688 (52.4%)                                            │
│                                                                             │
│   AGE GROUP (0.0% missing)                                                  │
│   ├── 18-44:       8,234 (18.2%)                                            │
│   ├── 45-64:      15,678 (34.7%)                                            │
│   └── 65+:        21,319 (47.1%)                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1.3 OUTCOME RATES BY SENSITIVE ATTRIBUTE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RACE (Reference: White)                       Chi-square p < 0.001        │
│   ┌─────────────┬─────────┬──────────────┬────────────┬──────────────────┐  │
│   │ Group       │ N       │ Outcome Rate │ Rate Ratio │ 95% CI           │  │
│   ├─────────────┼─────────┼──────────────┼────────────┼──────────────────┤  │
│   │ White [REF] │ 24,102  │ 10.2%        │ 1.00       │ --               │  │
│   │ Black       │ 12,445  │ 15.8%        │ 1.55       │ (1.42, 1.68)     │  │
│   │ Hispanic    │  5,874  │ 13.1%        │ 1.28       │ (1.14, 1.44)     │  │
│   │ Asian       │  1,856  │  9.4%        │ 0.92       │ (0.77, 1.10)     │  │
│   │ Other       │    954  │ 11.7%        │ 1.15       │ (0.92, 1.43)     │  │
│   └─────────────┴─────────┴──────────────┴────────────┴──────────────────┘  │
│                                                                             │
│   ⚠️ NOTE: These are DESCRIPTIVE differences in baseline outcome rates.     │
│   Differences may reflect true clinical variation, social determinants,     │
│   or data collection patterns. Interpret with clinical context.             │
│                                                                             │
│   SEX (Reference: Male)                         Chi-square p = 0.23         │
│   ┌─────────────┬─────────┬──────────────┬────────────┬──────────────────┐  │
│   │ Group       │ N       │ Outcome Rate │ Rate Ratio │ 95% CI           │  │
│   ├─────────────┼─────────┼──────────────┼────────────┼──────────────────┤  │
│   │ Male [REF]  │ 21,543  │ 12.6%        │ 1.00       │ --               │  │
│   │ Female      │ 23,688  │ 12.2%        │ 0.97       │ (0.91, 1.03)     │  │
│   └─────────────┴─────────┴──────────────┴────────────┴──────────────────┘  │
│                                                                             │
│   AGE GROUP (Reference: 18-44)                  Chi-square p < 0.001        │
│   ┌─────────────┬─────────┬──────────────┬────────────┬──────────────────┐  │
│   │ Group       │ N       │ Outcome Rate │ Rate Ratio │ 95% CI           │  │
│   ├─────────────┼─────────┼──────────────┼────────────┼──────────────────┤  │
│   │ 18-44 [REF] │  8,234  │  6.2%        │ 1.00       │ --               │  │
│   │ 45-64       │ 15,678  │ 10.8%        │ 1.74       │ (1.54, 1.97)     │  │
│   │ 65+         │ 21,319  │ 15.9%        │ 2.56       │ (2.29, 2.87)     │  │
│   └─────────────┴─────────┴──────────────┴────────────┴──────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1.4 MODEL PREDICTION DISTRIBUTION                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Overall Predictions                                                       │
│   ├── Mean (SD):     0.124 (0.098)                                          │
│   ├── Median:        0.093                                                  │
│   ├── Range:         [0.002, 0.847]                                         │
│   └── IQR:           [0.054, 0.162]                                         │
│                                                                             │
│   By Actual Outcome                                                         │
│   ├── Outcome = 1:   Mean = 0.287 (SD = 0.156)                              │
│   └── Outcome = 0:   Mean = 0.101 (SD = 0.067)                              │
│                                                                             │
│   [HISTOGRAM VISUALIZATION HERE]                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1.5 PREDICTION DISTRIBUTION BY SENSITIVE ATTRIBUTE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RACE                                                                      │
│   ┌─────────────┬─────────┬────────────────┬────────────────┐               │
│   │ Group       │ N       │ Pred Mean (SD) │ Pred Median    │               │
│   ├─────────────┼─────────┼────────────────┼────────────────┤               │
│   │ White       │ 24,102  │ 0.108 (0.089)  │ 0.082          │               │
│   │ Black       │ 12,445  │ 0.156 (0.112)  │ 0.124          │               │
│   │ Hispanic    │  5,874  │ 0.131 (0.095)  │ 0.103          │               │
│   │ Asian       │  1,856  │ 0.098 (0.078)  │ 0.076          │               │
│   │ Other       │    954  │ 0.119 (0.091)  │ 0.094          │               │
│   └─────────────┴─────────┴────────────────┴────────────────┘               │
│                                                                             │
│   ⚠️ NOTE: Higher mean predictions for Black patients may reflect:          │
│   (a) higher true baseline risk, (b) model bias, or (c) both.               │
│   Fairness metrics in Section 3 help distinguish these.                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Overall Model Performance Module (TRIPOD+AI Compliant)

```python
# faircareai/metrics/performance.py
"""
Overall model performance metrics following TRIPOD+AI guidelines.

This section answers: "Does this model work?" before we ask "Is it fair?"

References:
- TRIPOD+AI: Collins et al. (2024) BMJ
- Calibration: Van Calster et al. (2019) 
- Decision Curve Analysis: Vickers et al. (2006)
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, precision_recall_curve, roc_curve,
    precision_score, recall_score, f1_score
)
from sklearn.calibration import calibration_curve
from scipy import stats

def compute_overall_performance(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    thresholds_to_evaluate: Optional[List[float]] = None,
    bootstrap_ci: bool = True,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95
) -> Dict:
    """
    Compute comprehensive model performance metrics per TRIPOD+AI.
    
    Parameters
    ----------
    y_true : array
        True binary outcomes (0/1)
    y_prob : array
        Predicted probabilities
    threshold : float
        Primary decision threshold for classification metrics
    thresholds_to_evaluate : list, optional
        Additional thresholds for sensitivity analysis
    bootstrap_ci : bool
        Calculate bootstrap confidence intervals
    n_bootstrap : int
        Number of bootstrap iterations
    ci_level : float
        Confidence interval level (default 0.95)
        
    Returns
    -------
    dict with discrimination, calibration, classification, and DCA metrics
    """
    results = {}
    
    # =========================================================================
    # 2.1 DISCRIMINATION METRICS
    # =========================================================================
    results["discrimination"] = compute_discrimination_metrics(
        y_true, y_prob, bootstrap_ci, n_bootstrap, ci_level
    )
    
    # =========================================================================
    # 2.2 CALIBRATION METRICS
    # =========================================================================
    results["calibration"] = compute_calibration_metrics(
        y_true, y_prob, n_bins=10
    )
    
    # =========================================================================
    # 2.3 CLASSIFICATION METRICS AT THRESHOLD
    # =========================================================================
    results["classification_at_threshold"] = compute_classification_at_threshold(
        y_true, y_prob, threshold, bootstrap_ci, n_bootstrap, ci_level
    )
    
    # =========================================================================
    # 2.4 THRESHOLD SENSITIVITY ANALYSIS
    # =========================================================================
    if thresholds_to_evaluate is None:
        thresholds_to_evaluate = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    results["threshold_analysis"] = compute_threshold_analysis(
        y_true, y_prob, thresholds_to_evaluate
    )
    
    # =========================================================================
    # 2.5 DECISION CURVE ANALYSIS
    # =========================================================================
    results["decision_curve"] = compute_decision_curve_analysis(
        y_true, y_prob, thresholds=np.arange(0.01, 0.99, 0.01)
    )
    
    # =========================================================================
    # 2.6 CONFUSION MATRIX
    # =========================================================================
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    results["confusion_matrix"] = {
        "threshold": threshold,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "total": int(tp + fp + tn + fn)
    }
    
    # Primary threshold used
    results["primary_threshold"] = threshold
    
    return results


def compute_discrimination_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    bootstrap_ci: bool = True,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95
) -> Dict:
    """
    Compute discrimination metrics with confidence intervals.
    
    TRIPOD+AI items 10a, 10b: Report discrimination measures with uncertainty.
    """
    # Point estimates
    auroc = roc_auc_score(y_true, y_prob)
    auprc = average_precision_score(y_true, y_prob)
    
    results = {
        "auroc": auroc,
        "auprc": auprc,
        "prevalence": float(y_true.mean()),  # Needed to interpret AUPRC
    }
    
    # Bootstrap confidence intervals
    if bootstrap_ci:
        auroc_boots = []
        auprc_boots = []
        
        rng = np.random.default_rng(42)
        n = len(y_true)
        
        for _ in range(n_bootstrap):
            idx = rng.choice(n, size=n, replace=True)
            y_true_boot = y_true[idx]
            y_prob_boot = y_prob[idx]
            
            # Skip if only one class in bootstrap sample
            if len(np.unique(y_true_boot)) < 2:
                continue
            
            auroc_boots.append(roc_auc_score(y_true_boot, y_prob_boot))
            auprc_boots.append(average_precision_score(y_true_boot, y_prob_boot))
        
        alpha = (1 - ci_level) / 2
        
        results["auroc_ci"] = (
            float(np.percentile(auroc_boots, alpha * 100)),
            float(np.percentile(auroc_boots, (1 - alpha) * 100))
        )
        results["auroc_ci_fmt"] = f"({results['auroc_ci'][0]:.3f}, {results['auroc_ci'][1]:.3f})"
        
        results["auprc_ci"] = (
            float(np.percentile(auprc_boots, alpha * 100)),
            float(np.percentile(auprc_boots, (1 - alpha) * 100))
        )
        results["auprc_ci_fmt"] = f"({results['auprc_ci'][0]:.3f}, {results['auprc_ci'][1]:.3f})"
    
    # ROC curve data for plotting
    fpr, tpr, roc_thresholds = roc_curve(y_true, y_prob)
    results["roc_curve"] = {
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": roc_thresholds.tolist()
    }
    
    # PR curve data for plotting
    precision, recall, pr_thresholds = precision_recall_curve(y_true, y_prob)
    results["pr_curve"] = {
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "thresholds": pr_thresholds.tolist()
    }
    
    return results


def compute_calibration_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> Dict:
    """
    Compute calibration metrics and data for calibration plot.
    
    TRIPOD+AI item 10d: Report calibration measures.
    """
    # Brier score (lower is better, 0 = perfect)
    brier = brier_score_loss(y_true, y_prob)
    
    # Calibration curve (for plotting)
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy='uniform')
    
    # Calibration slope and intercept via logistic regression
    from sklearn.linear_model import LogisticRegression
    
    # Clip to avoid log(0)
    y_prob_clipped = np.clip(y_prob, 1e-10, 1 - 1e-10)
    log_odds = np.log(y_prob_clipped / (1 - y_prob_clipped)).reshape(-1, 1)
    
    lr = LogisticRegression(penalty=None, solver='lbfgs')
    lr.fit(log_odds, y_true)
    
    calibration_slope = float(lr.coef_[0][0])
    calibration_intercept = float(lr.intercept_[0])
    
    # Observed/Expected ratio (O:E)
    expected = y_prob.sum()
    observed = y_true.sum()
    oe_ratio = observed / expected if expected > 0 else np.nan
    
    # Integrated Calibration Index (ICI) - mean absolute calibration error
    ici = float(np.mean(np.abs(prob_true - prob_pred)))
    
    results = {
        "brier_score": brier,
        "calibration_slope": calibration_slope,
        "calibration_intercept": calibration_intercept,
        "oe_ratio": oe_ratio,
        "ici": ici,
        "calibration_curve": {
            "prob_true": prob_true.tolist(),
            "prob_pred": prob_pred.tolist(),
            "n_bins": n_bins
        },
        "interpretation": {
            "slope": "ideal=1.0; <1=overfitting, >1=underfitting",
            "intercept": "ideal=0.0; <0=overestimation, >0=underestimation",
            "brier": "ideal=0.0; lower is better; max=1.0"
        }
    }
    
    return results


def compute_classification_at_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
    bootstrap_ci: bool = True,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95
) -> Dict:
    """
    Compute classification metrics at a specific threshold.
    
    This is what the data scientist sets as their "high risk" cutoff.
    """
    y_pred = (y_prob >= threshold).astype(int)
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    # Core metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    f1 = 2 * ppv * sensitivity / (ppv + sensitivity) if (ppv + sensitivity) > 0 else 0
    
    # Likelihood ratios
    plr = sensitivity / (1 - specificity) if (1 - specificity) > 0 else np.inf
    nlr = (1 - sensitivity) / specificity if specificity > 0 else np.inf
    
    # Number needed to evaluate
    nne = 1 / ppv if ppv > 0 else np.inf
    
    n_total = tp + tn + fp + fn
    
    results = {
        "threshold": threshold,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "accuracy": accuracy,
        "f1_score": f1,
        "positive_likelihood_ratio": plr,
        "negative_likelihood_ratio": nlr,
        "number_needed_to_evaluate": nne,
        "n_predicted_positive": int(tp + fp),
        "n_predicted_negative": int(tn + fn),
        "pct_flagged": (tp + fp) / n_total * 100,
        "n_true_positive": int(tp),
        "n_false_positive": int(fp),
        "n_true_negative": int(tn),
        "n_false_negative": int(fn)
    }
    
    # Bootstrap CIs
    if bootstrap_ci:
        sens_boots, spec_boots, ppv_boots, npv_boots = [], [], [], []
        rng = np.random.default_rng(42)
        n = len(y_true)
        
        for _ in range(n_bootstrap):
            idx = rng.choice(n, size=n, replace=True)
            y_true_boot = y_true[idx]
            y_pred_boot = (y_prob[idx] >= threshold).astype(int)
            
            tn_b, fp_b, fn_b, tp_b = confusion_matrix(
                y_true_boot, y_pred_boot, labels=[0, 1]
            ).ravel()
            
            sens_boots.append(tp_b / (tp_b + fn_b) if (tp_b + fn_b) > 0 else 0)
            spec_boots.append(tn_b / (tn_b + fp_b) if (tn_b + fp_b) > 0 else 0)
            ppv_boots.append(tp_b / (tp_b + fp_b) if (tp_b + fp_b) > 0 else 0)
            npv_boots.append(tn_b / (tn_b + fn_b) if (tn_b + fn_b) > 0 else 0)
        
        alpha = (1 - ci_level) / 2
        for metric, boots in [("sensitivity", sens_boots), ("specificity", spec_boots),
                              ("ppv", ppv_boots), ("npv", npv_boots)]:
            results[f"{metric}_ci"] = (
                float(np.percentile(boots, alpha * 100)),
                float(np.percentile(boots, (1 - alpha) * 100))
            )
    
    return results


def compute_threshold_analysis(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: List[float]
) -> Dict:
    """
    Compute classification metrics across multiple thresholds.
    
    Allows data scientist to TOGGLE and see impact of different cutoffs.
    """
    results = {"thresholds": []}
    n_total = len(y_true)
    
    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        
        results["thresholds"].append({
            "threshold": thresh,
            "sensitivity": tp / (tp + fn) if (tp + fn) > 0 else 0,
            "specificity": tn / (tn + fp) if (tn + fp) > 0 else 0,
            "ppv": tp / (tp + fp) if (tp + fp) > 0 else 0,
            "npv": tn / (tn + fn) if (tn + fn) > 0 else 0,
            "n_flagged": int(tp + fp),
            "pct_flagged": (tp + fp) / n_total * 100,
            "n_true_positive": int(tp),
            "n_false_positive": int(fp),
            "n_false_negative": int(fn)
        })
    
    return results


def compute_decision_curve_analysis(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: np.ndarray = None
) -> Dict:
    """
    Compute Decision Curve Analysis (DCA) for clinical utility assessment.
    
    DCA answers: "At what threshold range does this model provide net benefit
    over treat-all or treat-none strategies?"
    
    Reference: Vickers AJ, Elkin EB. Med Decis Making. 2006.
    """
    if thresholds is None:
        thresholds = np.arange(0.01, 0.99, 0.01)
    
    n = len(y_true)
    prevalence = y_true.mean()
    
    results = {
        "thresholds": thresholds.tolist(),
        "net_benefit_model": [],
        "net_benefit_treat_all": [],
        "net_benefit_treat_none": []
    }
    
    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        
        if thresh < 1:
            weight = thresh / (1 - thresh)
            nb_model = (tp / n) - (fp / n) * weight
            nb_treat_all = prevalence - (1 - prevalence) * weight
        else:
            nb_model = 0
            nb_treat_all = 0
        
        nb_treat_none = 0
        
        results["net_benefit_model"].append(float(nb_model))
        results["net_benefit_treat_all"].append(float(nb_treat_all))
        results["net_benefit_treat_none"].append(float(nb_treat_none))
    
    # Find useful range
    useful_range = []
    for i, thresh in enumerate(thresholds):
        nb_model = results["net_benefit_model"][i]
        nb_all = results["net_benefit_treat_all"][i]
        nb_none = results["net_benefit_treat_none"][i]
        
        if nb_model > max(nb_all, nb_none):
            useful_range.append(thresh)
    
    results["useful_threshold_range"] = {
        "min": float(min(useful_range)) if useful_range else None,
        "max": float(max(useful_range)) if useful_range else None
    }
    
    return results
```

### Report Section 2: Overall Model Performance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               SECTION 2: OVERALL MODEL PERFORMANCE (TRIPOD+AI)              │
│               This section answers: "Does this model work?"                 │
│               BEFORE we ask: "Is it fair?"                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2.1 DISCRIMINATION                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Metric        │ Value   │ 95% CI           │ Interpretation         │   │
│   ├───────────────┼─────────┼──────────────────┼────────────────────────┤   │
│   │ AUROC         │ 0.742   │ (0.728, 0.756)   │ Acceptable             │   │
│   │ AUPRC         │ 0.389   │ (0.361, 0.418)   │ (Prevalence: 12.4%)    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [ROC CURVE PLOT]                   [PRECISION-RECALL CURVE PLOT]          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2.2 CALIBRATION                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Metric                │ Value   │ Ideal   │ Interpretation          │   │
│   ├───────────────────────┼─────────┼─────────┼─────────────────────────┤   │
│   │ Brier Score           │ 0.089   │ 0.000   │ Good (lower is better)  │   │
│   │ Calibration Slope     │ 0.94    │ 1.00    │ Slight overfitting      │   │
│   │ Calibration Intercept │ 0.02    │ 0.00    │ Slight underestimation  │   │
│   │ O:E Ratio             │ 1.03    │ 1.00    │ Well calibrated         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [CALIBRATION PLOT: Predicted vs Observed with LOESS smoother]             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2.3 CLASSIFICATION METRICS AT HIGH-RISK THRESHOLD                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   🎚️  THRESHOLD SELECTOR: [ 0.30 ]  ◄─── Data scientist sets this          │
│                                                                             │
│   At threshold = 0.30:                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Metric              │ Value     │ 95% CI           │ N               │   │
│   ├─────────────────────┼───────────┼──────────────────┼─────────────────┤   │
│   │ Sensitivity (TPR)   │ 68.4%     │ (65.2%, 71.6%)   │ 3,835 / 5,608   │   │
│   │ Specificity (TNR)   │ 72.1%     │ (71.4%, 72.8%)   │ 28,565 / 39,623 │   │
│   │ PPV (Precision)     │ 25.7%     │ (24.3%, 27.2%)   │ 3,835 / 14,893  │   │
│   │ NPV                 │ 94.2%     │ (93.8%, 94.5%)   │ 28,565 / 30,338 │   │
│   │ F1 Score            │ 0.374     │                  │                 │   │
│   │ Accuracy            │ 71.6%     │                  │                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   📊 Population Impact at this threshold:                                   │
│   ├── Flagged as High Risk:    14,893 patients (32.9%)                      │
│   ├── True Positives:           3,835 (correctly identified)                │
│   ├── False Positives:         11,058 (unnecessary flag)                    │
│   ├── False Negatives:          1,773 (missed cases)                        │
│   └── Number Needed to Evaluate: 3.9 (screen 3.9 to find 1 true positive)   │
│                                                                             │
│   Confusion Matrix at threshold = 0.30:                                     │
│                             Predicted                                       │
│                         Neg         Pos                                     │
│   Actual    Neg      28,565      11,058                                     │
│             Pos       1,773       3,835                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2.4 THRESHOLD SENSITIVITY ANALYSIS (Interactive Toggle)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   How do metrics change across different "high risk" cutoffs?               │
│                                                                             │
│   ┌──────────┬───────────┬───────────┬─────────┬─────────┬─────────────┐    │
│   │ Threshold│ Sensitivity│ Specificity│  PPV   │  NPV    │ % Flagged   │    │
│   ├──────────┼───────────┼───────────┼─────────┼─────────┼─────────────┤    │
│   │   0.10   │   92.3%   │   41.2%   │  18.2%  │  97.4%  │   62.1%     │    │
│   │   0.20   │   78.9%   │   61.4%   │  22.1%  │  95.3%  │   44.2%     │    │
│   │ ► 0.30   │   68.4%   │   72.1%   │  25.7%  │  94.2%  │   32.9%     │    │
│   │   0.40   │   54.2%   │   82.3%   │  30.8%  │  92.3%  │   21.8%     │    │
│   │   0.50   │   41.1%   │   89.4%   │  35.4%  │  90.1%  │   14.4%     │    │
│   └──────────┴───────────┴───────────┴─────────┴─────────┴─────────────┘    │
│                                                                             │
│   [INTERACTIVE PLOT: Metrics vs Threshold with slider]                      │
│                                                                             │
│   ⚠️ ADVISORY: Threshold selection depends on clinical context:             │
│   • High-stakes intervention → prioritize PPV (higher threshold)            │
│   • Screening/early detection → prioritize Sensitivity (lower threshold)    │
│   • Resource constraints → consider % Flagged workload                      │
│                                                                             │
│   This is a clinical decision — FairCareAI provides data, YOU decide.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2.5 DECISION CURVE ANALYSIS (Clinical Utility)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Does using this model improve outcomes vs. treat-all or treat-none?       │
│                                                                             │
│   [DECISION CURVE PLOT]                                                     │
│                                                                             │
│   Net Benefit                                                               │
│       │                                                                     │
│   0.15┤      ╭───── Model                                                   │
│       │     ╱                                                               │
│   0.10┤    ╱   ╲                                                            │
│       │   ╱     ╲                                                           │
│   0.05┤  ╱       ╲_____ Treat All                                           │
│       │ ╱                                                                   │
│   0.00┼─────────────────────────────── Treat None                           │
│       └──────────────────────────────────────────                           │
│       0.0   0.2   0.4   0.6   0.8   1.0                                     │
│                 Threshold Probability                                       │
│                                                                             │
│   ✅ Model provides net clinical benefit at thresholds: 0.08 - 0.52         │
│   ✅ At your threshold (0.30): Net benefit = 0.092 (useful)                 │
│                                                                             │
│   Reference: Vickers AJ, Elkin EB. Decision curve analysis: a novel method  │
│   for evaluating prediction models. Med Decis Making. 2006;26(6):565-74.    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Performance Visualization Module

```python
# faircareai/visualization/performance_charts.py
"""
Visualizations for Overall Model Performance section (TRIPOD+AI).
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_discrimination_curves(results) -> go.Figure:
    """Plot ROC and Precision-Recall curves side by side."""
    disc = results.overall_performance["discrimination"]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"ROC Curve (AUROC = {disc['auroc']:.3f})",
            f"Precision-Recall Curve (AUPRC = {disc['auprc']:.3f})"
        )
    )
    
    # ROC Curve
    fig.add_trace(
        go.Scatter(x=disc["roc_curve"]["fpr"], y=disc["roc_curve"]["tpr"],
                   mode="lines", name="Model", line=dict(color="#3498db", width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random",
                   line=dict(color="gray", dash="dash")),
        row=1, col=1
    )
    
    # PR Curve
    fig.add_trace(
        go.Scatter(x=disc["pr_curve"]["recall"], y=disc["pr_curve"]["precision"],
                   mode="lines", name="Model", line=dict(color="#e74c3c", width=2)),
        row=1, col=2
    )
    prevalence = disc["prevalence"]
    fig.add_trace(
        go.Scatter(x=[0, 1], y=[prevalence, prevalence], mode="lines",
                   name=f"Baseline ({prevalence:.1%})", line=dict(color="gray", dash="dash")),
        row=1, col=2
    )
    
    fig.update_layout(height=400, title_text="Discrimination Performance")
    return fig


def plot_calibration(results) -> go.Figure:
    """Plot calibration curve."""
    cal = results.overall_performance["calibration"]
    curve = cal["calibration_curve"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                             name="Perfect", line=dict(color="gray", dash="dash")))
    fig.add_trace(go.Scatter(x=curve["prob_pred"], y=curve["prob_true"],
                             mode="lines+markers", name="Model",
                             line=dict(color="#2ecc71", width=2)))
    
    fig.update_layout(
        title=f"Calibration (Slope={cal['calibration_slope']:.2f})",
        xaxis_title="Predicted Probability",
        yaxis_title="Observed Frequency",
        height=400
    )
    return fig


def plot_threshold_analysis(results, selected_threshold: float = None) -> go.Figure:
    """Interactive threshold analysis with toggle."""
    data = results.overall_performance["threshold_analysis"]["thresholds"]
    
    thresholds = [t["threshold"] for t in data]
    sens = [t["sensitivity"] for t in data]
    spec = [t["specificity"] for t in data]
    ppv = [t["ppv"] for t in data]
    pct_flagged = [t["pct_flagged"] / 100 for t in data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thresholds, y=sens, name="Sensitivity", line=dict(color="#3498db")))
    fig.add_trace(go.Scatter(x=thresholds, y=spec, name="Specificity", line=dict(color="#2ecc71")))
    fig.add_trace(go.Scatter(x=thresholds, y=ppv, name="PPV", line=dict(color="#e74c3c")))
    fig.add_trace(go.Scatter(x=thresholds, y=pct_flagged, name="% Flagged",
                             line=dict(color="#9b59b6", dash="dot")))
    
    if selected_threshold:
        fig.add_vline(x=selected_threshold, line_dash="dash", line_color="orange",
                      annotation_text=f"Selected: {selected_threshold}")
    
    fig.update_layout(title="Threshold Sensitivity Analysis",
                      xaxis_title="Threshold", yaxis_title="Value",
                      yaxis_range=[0, 1], height=400)
    return fig


def plot_decision_curve(results) -> go.Figure:
    """Plot Decision Curve Analysis."""
    dca = results.overall_performance["decision_curve"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dca["thresholds"], y=dca["net_benefit_model"],
                             name="Model", line=dict(color="#3498db", width=2)))
    fig.add_trace(go.Scatter(x=dca["thresholds"], y=dca["net_benefit_treat_all"],
                             name="Treat All", line=dict(color="#e74c3c", dash="dash")))
    fig.add_trace(go.Scatter(x=dca["thresholds"], y=dca["net_benefit_treat_none"],
                             name="Treat None", line=dict(color="gray", dash="dot")))
    
    useful = dca.get("useful_threshold_range", {})
    if useful.get("min") and useful.get("max"):
        fig.add_vrect(x0=useful["min"], x1=useful["max"],
                      fillcolor="green", opacity=0.1,
                      annotation_text="Model useful here")
    
    fig.update_layout(title="Decision Curve Analysis",
                      xaxis_title="Threshold", yaxis_title="Net Benefit", height=400)
    return fig
```

---

## Fairness Metrics Module

```python
# faircareai/metrics/fairness.py
import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.metrics import confusion_matrix

def compute_fairness_metrics(
    data: pd.DataFrame,
    pred_col: str,
    target_col: str,
    group_col: str,
    threshold: float = 0.5,
    reference: Optional[str] = None
) -> Dict:
    """
    Compute comprehensive fairness metrics.
    
    NOTE: These metrics inform decisions but do not dictate them.
    The data scientist and health system determine acceptable thresholds
    based on their clinical context and organizational values.
    
    Returns
    -------
    dict with keys:
        - demographic_parity_ratio
        - equalized_odds_diff (TPR and FPR differences)
        - predictive_parity_ratio (PPV ratio)
        - calibration_diff
    """
    results = {
        "demographic_parity_ratio": {},
        "tpr_diff": {},
        "fpr_diff": {},
        "equalized_odds_diff": {},
        "ppv_ratio": {},
        "calibration_diff": {}
    }
    
    data = data.copy()
    data["pred_binary"] = (data[pred_col] >= threshold).astype(int)
    
    groups = data[group_col].dropna().unique()
    
    # Compute per-group metrics
    group_metrics = {}
    for group in groups:
        mask = data[group_col] == group
        group_data = data[mask]
        
        y_true = group_data[target_col].values
        y_pred = group_data["pred_binary"].values
        y_prob = group_data[pred_col].values
        
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        
        group_metrics[group] = {
            "selection_rate": y_pred.mean(),
            "tpr": tp / (tp + fn) if (tp + fn) > 0 else 0,
            "fpr": fp / (fp + tn) if (fp + tn) > 0 else 0,
            "ppv": tp / (tp + fp) if (tp + fp) > 0 else 0,
            "calibration": y_true[y_pred == 1].mean() if y_pred.sum() > 0 else 0
        }
    
    # Determine reference group
    if reference is None:
        # Use majority group as reference
        reference = data[group_col].value_counts().idxmax()
    
    ref_metrics = group_metrics[reference]
    
    # Compute disparities relative to reference
    for group in groups:
        if group == reference:
            continue
        
        gm = group_metrics[group]
        
        # Demographic parity ratio
        if ref_metrics["selection_rate"] > 0:
            results["demographic_parity_ratio"][group] = (
                gm["selection_rate"] / ref_metrics["selection_rate"]
            )
        
        # TPR difference (equal opportunity)
        results["tpr_diff"][group] = gm["tpr"] - ref_metrics["tpr"]
        
        # FPR difference
        results["fpr_diff"][group] = gm["fpr"] - ref_metrics["fpr"]
        
        # Equalized odds (max of TPR and FPR diff)
        results["equalized_odds_diff"][group] = max(
            abs(results["tpr_diff"][group]),
            abs(results["fpr_diff"][group])
        )
        
        # PPV ratio (predictive parity)
        if ref_metrics["ppv"] > 0:
            results["ppv_ratio"][group] = gm["ppv"] / ref_metrics["ppv"]
        
        # Calibration difference
        results["calibration_diff"][group] = abs(
            gm["calibration"] - ref_metrics["calibration"]
        )
    
    results["reference_group"] = reference
    results["group_metrics"] = group_metrics
    
    return results
```

---

## Fairness Metric Decision Tree (CHAI-Grounded Recommendations)

```python
# faircareai/fairness/decision_tree.py
"""
evidence-based recommendations for fairness metric selection.

IMPORTANT: These are RECOMMENDATIONS based on CHAI framework and fairness 
literature, not requirements. The data scientist and health system make 
the final selection based on their clinical context, organizational values, 
and stakeholder input.

The impossibility theorem means no single metric is universally "correct" — 
this is inherently a value judgment that humans must make.
"""
from typing import Optional, Dict
from ..core.config import UseCaseType, FairnessMetric

DECISION_TREE = {
    UseCaseType.INTERVENTION_TRIGGER: {
        "recommended": FairnessMetric.EQUALIZED_ODDS,
        "rationale": """
            When model triggers an intervention (e.g., care management outreach, 
            palliative care consult), equalizing true positive rates ensures all 
            groups receive equal benefit when truly at risk. Equalizing false 
            positive rates prevents unequal burden of unnecessary intervention.
        """,
        "alternatives": [FairnessMetric.EQUAL_OPPORTUNITY],
        "considerations": [FairnessMetric.DEMOGRAPHIC_PARITY],
        "considerations_note": "Demographic parity may over/under-intervene based on base rates — "
                              "but may be appropriate if historical access disparities exist"
    },
    
    UseCaseType.RISK_COMMUNICATION: {
        "recommended": FairnessMetric.CALIBRATION,
        "rationale": """
            When model communicates risk to patients/providers for shared decision-making,
            calibration ensures predicted probabilities are accurate across groups.
            A patient told they have 30% risk should truly have 30% risk regardless of group.
        """,
        "alternatives": [FairnessMetric.PREDICTIVE_PARITY],
        "considerations": [FairnessMetric.DEMOGRAPHIC_PARITY],
        "considerations_note": "Risk communication should generally reflect true risk, "
                              "but context may warrant adjustments"
    },
    
    UseCaseType.RESOURCE_ALLOCATION: {
        "recommended": FairnessMetric.DEMOGRAPHIC_PARITY,
        "rationale": """
            When model allocates limited resources (e.g., care coordination slots, 
            preventive screening), demographic parity ensures equal access across groups,
            particularly important when historical access disparities exist.
        """,
        "alternatives": [FairnessMetric.EQUALIZED_ODDS],
        "considerations": [],
        "note": "Health system should decide whether equal allocation or need-based allocation aligns with their equity goals"
    },
    
    UseCaseType.SCREENING: {
        "recommended": FairnessMetric.EQUAL_OPPORTUNITY,
        "rationale": """
            For screening applications, equal opportunity (equal TPR) ensures 
            those with disease are equally likely to be detected across groups.
            This prioritizes sensitivity equity over specificity equity.
        """,
        "alternatives": [FairnessMetric.EQUALIZED_ODDS],
        "considerations": [],
        "note": "Health system should balance detection equity with cost of false positives in their setting"
    },
    
    UseCaseType.DIAGNOSIS_SUPPORT: {
        "recommended": FairnessMetric.CALIBRATION,
        "rationale": """
            Diagnostic support tools should provide well-calibrated probabilities
            that clinicians can interpret consistently across patient groups.
        """,
        "alternatives": [FairnessMetric.EQUALIZED_ODDS, FairnessMetric.PREDICTIVE_PARITY],
        "considerations": [],
        "note": "Health system may want to evaluate multiple metrics for comprehensive assessment"
    }
}

def recommend_fairness_metric(use_case: Optional[UseCaseType]) -> Dict:
    """
    Provide evidence-based recommendation for fairness metric based on use case.
    
    IMPORTANT: This is a RECOMMENDATION, not a requirement. The data scientist
    and health system make the final selection based on their context.
    
    Returns
    -------
    dict with recommendation details and rationale
    """
    if use_case is None:
        return {
            "status": "needs_input",
            "message": "Please specify use_case_type to get fairness metric recommendation",
            "options": [ut.value for ut in UseCaseType],
            "disclaimer": "Recommendations are evidence-based guidance. Final selection is yours."
        }
    
    if use_case not in DECISION_TREE:
        return {
            "status": "unknown",
            "message": f"No recommendation available for use case: {use_case.value}",
            "disclaimer": "You may still select any fairness metric with appropriate justification."
        }
    
    rec = DECISION_TREE[use_case]
    
    return {
        "status": "recommendation",
        "use_case": use_case.value,
        "recommended_metric": rec["recommended"].value,
        "rationale": rec["rationale"].strip(),
        "alternatives": [m.value for m in rec.get("alternatives", [])],
        "considerations": [m.value for m in rec.get("considerations", [])],
        "considerations_note": rec.get("considerations_note", ""),
        "note": rec.get("note", ""),
        "disclaimer": "This is a evidence-based RECOMMENDATION. The data scientist and "
                     "health system make the final selection. Any metric can be chosen "
                     "with appropriate clinical justification."
    }


def get_impossibility_warning() -> str:
    """Return impossibility theorem warning text."""
    return """
    ════════════════════════════════════════════════════════════════════════════
    ⚠️  FAIRNESS IMPOSSIBILITY THEOREM — READ BEFORE PROCEEDING
    ════════════════════════════════════════════════════════════════════════════
    
    It is MATHEMATICALLY IMPOSSIBLE to satisfy all fairness metrics simultaneously
    when base rates differ between groups (Chouldechova 2017, Kleinberg et al. 2016).
    
    This means:
    • There is NO "correct" fairness metric — only trade-offs
    • Selecting a primary metric is a VALUE JUDGMENT, not a technical decision
    • Different stakeholders may reasonably disagree on the right choice
    
    FairCareAI provides evidence-based recommendations based on use case type,
    but YOU AND YOUR HEALTH SYSTEM must make the final decision based on:
    
    1. The clinical/operational context
    2. The downstream impact of different error types (FP vs FN)
    3. Organizational equity goals and values
    4. Stakeholder input (patients, clinicians, community)
    5. Regulatory and policy considerations
    
    Document your choice and rationale — this is required for CHAI compliance
    and demonstrates thoughtful governance to oversight committees.
    
    ════════════════════════════════════════════════════════════════════════════
    """
```

---

## CHAI Evidence Generator

```python
# faircareai/chai/evidence_generator.py
from typing import Dict, List, Any
from ..core.config import FairnessConfig
from ..core.results import AuditResults

# Mapping of report sections to CHAI RAIC criteria
CHAI_CRITERIA_MAP = {
    "model_identity": {
        "AC1.CR1": "Evidence that AI solution directly targets the stated problem",
        "AC1.CR3": "Well-defined target population for the model",
        "AC1.CR4": "User base of the AI solution clearly defined",
        "AC1.CR100": "Description of model purpose, limitations, and safety risks"
    },
    "data_specification": {
        "AC1.CR33": "Size of training/testing datasets adequate for target population",
        "AC1.CR34": "Documentation of data sources, purposes, and consent",
        "AC1.CR64": "Comprehensiveness of data evaluated for subgroup performance",
        "AC1.CR68": "Missing data disparities between subgroups addressed"
    },
    "sensitive_attributes": {
        "AC1.CR48": "Protected characteristics used explicitly or implicitly",
        "AC1.CR49": "Clinical justification for use of protected characteristics",
        "AC1.CR50": "Direction and magnitude of protected characteristic effects documented",
        "AC1.CR54": "Proxies or composite scores identified",
        "AC1.CR55": "Proxies evaluated for bias across subgroups"
    },
    "overall_performance": {
        "AC1.CR73": "Model performance metrics clearly documented",
        "AC1.CR79": "Clear decision thresholds established",
        "AC1.CR83": "Confidence intervals documented",
        "AC1.CR85": "Confusion/error matrix generated",
        "AC1.CR88": "Model calibration evaluated across sample and subgroups"
    },
    "fairness_assessment": {
        "AC1.CR80": "Limitations to interpretability/generalizability documented",
        "AC1.CR81": "Unaddressable biases in subgroup performance documented",
        "AC1.CR82": "Sample size limitations for parity analyses documented",
        "AC1.CR90": "Counterfactual tests conducted with/without protected attributes",
        "AC1.CR91": "Calibration independent of protected classes",
        "AC1.CR92": "Parity measures selected considering impact of errors",
        "AC1.CR93": "Selected parity measures consistent with predefined fairness definition",
        "AC1.CR96": "Model performance/parity evaluated using locally representative data"
    },
    "governance": {
        "AC1.CR101": "Plan to evaluate impartiality in resource distribution/outcomes",
        "AC1.CR102": "Real-world outcome measure defined with justification",
        "AC1.CR103": "Real-world outcome available for evaluation",
        "AC1.CR104": "Real-world outcomes compared for parity across subgroups",
        "AC1.CR134": "Model procedures, risks, benefits reviewed by stakeholders"
    }
}

# CRITICAL: Advisory disclaimer for all outputs
GOVERNANCE_DISCLAIMER = """
════════════════════════════════════════════════════════════════════════════════
IMPORTANT: ADVISORY GUIDANCE ONLY

This report provides evidence-based analysis and recommendations to support 
governance decisions. It does NOT mandate any particular action.

FINAL DECISIONS REST WITH:
• The data scientist who understands the model and its context
• The health system governance committee with clinical and operational expertise
• Organizational leadership with authority over deployment decisions

FairCareAI identifies considerations per CHAI RAIC criteria. How to weigh these 
considerations against organizational context, risk tolerance, and clinical 
priorities is a human judgment that cannot be automated.

Thresholds used in this report are evidence-based defaults. Health systems 
should establish their own thresholds based on their specific context.
════════════════════════════════════════════════════════════════════════════════
"""


def generate_evidence(
    config: FairnessConfig,
    results: AuditResults,
    sensitive_attrs: List[Any]
) -> Dict:
    """Generate CHAI RAIC evidence snippets for each criteria."""
    
    evidence = {}
    
    # Model Identity Evidence
    evidence["AC1.CR1"] = {
        "criteria": CHAI_CRITERIA_MAP["model_identity"]["AC1.CR1"],
        "status": "provided" if config.intended_use else "missing",
        "evidence": f"Intended use: {config.intended_use}" if config.intended_use else "Not documented"
    }
    
    evidence["AC1.CR3"] = {
        "criteria": CHAI_CRITERIA_MAP["model_identity"]["AC1.CR3"],
        "status": "provided" if config.intended_population else "missing",
        "evidence": f"Target population: {config.intended_population}" if config.intended_population else "Not documented"
    }
    
    # Data Specification Evidence
    evidence["AC1.CR33"] = {
        "criteria": CHAI_CRITERIA_MAP["data_specification"]["AC1.CR33"],
        "status": "provided",
        "evidence": f"Total N: {results.data_summary.get('n_total', 'N/A'):,}, "
                   f"Positive: {results.data_summary.get('n_positive', 'N/A'):,}, "
                   f"Prevalence: {results.data_summary.get('prevalence', 0):.1%}"
    }
    
    evidence["AC1.CR64"] = {
        "criteria": CHAI_CRITERIA_MAP["data_specification"]["AC1.CR64"],
        "status": "provided",
        "evidence": _format_subgroup_ns(results.subgroup_performance)
    }
    
    evidence["AC1.CR68"] = {
        "criteria": CHAI_CRITERIA_MAP["data_specification"]["AC1.CR68"],
        "status": "provided",
        "evidence": _format_missing_rates(results.data_summary.get("attributes", {}))
    }
    
    # Sensitive Attributes Evidence
    attr_list = [f"{a.name} (ref: {a.reference})" for a in sensitive_attrs]
    evidence["AC1.CR48"] = {
        "criteria": CHAI_CRITERIA_MAP["sensitive_attributes"]["AC1.CR48"],
        "status": "provided",
        "evidence": f"Sensitive attributes analyzed: {', '.join(attr_list)}"
    }
    
    justifications = [a.clinical_justification for a in sensitive_attrs if a.clinical_justification]
    evidence["AC1.CR49"] = {
        "criteria": CHAI_CRITERIA_MAP["sensitive_attributes"]["AC1.CR49"],
        "status": "provided" if justifications else "missing",
        "evidence": "; ".join(justifications) if justifications else "No clinical justifications provided"
    }
    
    # Performance Evidence
    perf = results.overall_performance
    evidence["AC1.CR73"] = {
        "criteria": CHAI_CRITERIA_MAP["overall_performance"]["AC1.CR73"],
        "status": "provided",
        "evidence": f"AUROC: {perf.get('auroc', 'N/A'):.3f}, "
                   f"AUPRC: {perf.get('auprc', 'N/A'):.3f}, "
                   f"Brier: {perf.get('brier_score', 'N/A'):.3f}"
    }
    
    evidence["AC1.CR88"] = {
        "criteria": CHAI_CRITERIA_MAP["overall_performance"]["AC1.CR88"],
        "status": "provided",
        "evidence": _format_calibration_evidence(results.subgroup_performance)
    }
    
    # Fairness Evidence
    evidence["AC1.CR92"] = {
        "criteria": CHAI_CRITERIA_MAP["fairness_assessment"]["AC1.CR92"],
        "status": "provided" if config.primary_fairness_metric else "missing",
        "evidence": f"Primary metric: {config.primary_fairness_metric.value if config.primary_fairness_metric else 'NOT SPECIFIED'}"
    }
    
    evidence["AC1.CR93"] = {
        "criteria": CHAI_CRITERIA_MAP["fairness_assessment"]["AC1.CR93"],
        "status": "provided" if config.fairness_justification else "missing",
        "evidence": config.fairness_justification if config.fairness_justification else "NOT PROVIDED - REQUIRED"
    }
    
    # Document limitations
    warnings = [f for f in results.flags if f["level"] == "warning"]
    evidence["AC1.CR82"] = {
        "criteria": CHAI_CRITERIA_MAP["fairness_assessment"]["AC1.CR82"],
        "status": "provided",
        "evidence": _format_sample_size_limitations(warnings)
    }
    
    evidence["AC1.CR80"] = {
        "criteria": CHAI_CRITERIA_MAP["fairness_assessment"]["AC1.CR80"],
        "status": "provided",
        "evidence": _format_fairness_limitations(warnings)
    }
    
    # Governance
    evidence["AC1.CR134"] = {
        "criteria": CHAI_CRITERIA_MAP["governance"]["AC1.CR134"],
        "status": "ready_for_review",
        "evidence": f"Recommendation: {results.governance_recommendation.get('status', 'N/A')} - "
                   f"{results.governance_recommendation.get('recommendation', '')}"
    }
    
    return evidence


def _format_subgroup_ns(subgroup_perf: Dict) -> str:
    """Format subgroup sample sizes."""
    lines = []
    for attr, groups in subgroup_perf.items():
        group_strs = [f"{g}: n={m['n']:,}" for g, m in groups.items()]
        lines.append(f"{attr}: {', '.join(group_strs)}")
    return "; ".join(lines)


def _format_missing_rates(attributes: Dict) -> str:
    """Format missing data rates."""
    rates = [f"{name}: {info.get('missing_rate', 0):.1%}" 
             for name, info in attributes.items()]
    return f"Missing rates - {', '.join(rates)}"


def _format_calibration_evidence(subgroup_perf: Dict) -> str:
    """Format calibration evidence across subgroups."""
    # Implementation depends on what calibration metrics you store
    return "Calibration evaluated across all subgroups - see report for details"


def _format_sample_size_limitations(warnings: List[Dict]) -> str:
    """Format sample size limitation warnings."""
    size_warnings = [w for w in warnings if w.get("category") == "sample_size"]
    if not size_warnings:
        return "No sample size limitations identified"
    
    return "; ".join([w["message"] for w in size_warnings])


def _format_fairness_limitations(warnings: List[Dict]) -> str:
    """Format fairness metric limitation warnings."""
    fairness_warnings = [w for w in warnings if w.get("category") == "fairness"]
    if not fairness_warnings:
        return "No fairness metric violations identified"
    
    return "; ".join([w["message"] for w in fairness_warnings])


def export_evidence_markdown(evidence: Dict, path: str):
    """Export evidence as markdown for CHAI checklist."""
    lines = [
        "# CHAI RAIC Evidence Documentation",
        "",
        "Generated by FairCareAI",
        "",
        "---",
        ""
    ]
    
    for criteria_id, data in sorted(evidence.items()):
        status_emoji = "✅" if data["status"] == "provided" else "⚠️" if data["status"] == "missing" else "📋"
        lines.extend([
            f"## {criteria_id}: {data['criteria']}",
            "",
            f"**Status:** {status_emoji} {data['status'].upper()}",
            "",
            f"**Evidence:**",
            f"> {data['evidence']}",
            "",
            "---",
            ""
        ])
    
    with open(path, "w") as f:
        f.write("\n".join(lines))
```

---

## Visualization (Plotly Example)

### Descriptive Statistics Visualizations

```python
# faircareai/visualization/descriptive_charts.py
"""
Visualizations for Table 1 / Descriptive Statistics section.
These provide essential context BEFORE diving into fairness metrics.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict

def plot_cohort_overview(results) -> go.Figure:
    """
    Create cohort overview visualization.
    
    Shows:
    - Total N with outcome breakdown
    - Sensitive attribute distributions
    - Outcome rates by attribute
    """
    desc = results.descriptive_stats
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Cohort Outcome Distribution",
            "Sensitive Attribute Distributions",
            "Outcome Rate by Race",
            "Outcome Rate by Age Group"
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}]
        ]
    )
    
    # 1. Outcome pie chart
    cohort = desc["cohort_overview"]
    fig.add_trace(
        go.Pie(
            labels=["No Outcome", "Outcome"],
            values=[cohort["n_negative"], cohort["n_positive"]],
            hole=0.4,
            marker_colors=["#2ecc71", "#e74c3c"],
            textinfo="label+percent"
        ),
        row=1, col=1
    )
    
    # 2. Attribute distribution bars
    for attr_name, attr_data in desc["attribute_distributions"].items():
        groups = list(attr_data["distribution"].keys())
        counts = [attr_data["distribution"][g]["n"] for g in groups]
        
        fig.add_trace(
            go.Bar(name=attr_name, x=groups, y=counts),
            row=1, col=2
        )
    
    # 3. Outcome rates by race
    if "race" in desc["outcome_by_attribute"]:
        race_data = desc["outcome_by_attribute"]["race"]["groups"]
        groups = list(race_data.keys())
        rates = [race_data[g]["outcome_rate"] * 100 for g in groups]
        colors = ["#3498db" if not race_data[g].get("is_reference") else "#2c3e50" for g in groups]
        
        fig.add_trace(
            go.Bar(
                x=groups, 
                y=rates,
                marker_color=colors,
                text=[f"{r:.1f}%" for r in rates],
                textposition="outside"
            ),
            row=2, col=1
        )
    
    # 4. Outcome rates by age group
    if "age_group" in desc["outcome_by_attribute"]:
        age_data = desc["outcome_by_attribute"]["age_group"]["groups"]
        groups = list(age_data.keys())
        rates = [age_data[g]["outcome_rate"] * 100 for g in groups]
        
        fig.add_trace(
            go.Bar(
                x=groups, 
                y=rates,
                marker_color="#9b59b6",
                text=[f"{r:.1f}%" for r in rates],
                textposition="outside"
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=700,
        title_text="Cohort Descriptive Statistics",
        showlegend=False
    )
    
    return fig


def plot_prediction_distribution(results) -> go.Figure:
    """
    Plot model prediction score distribution.
    
    Shows:
    - Overall distribution histogram
    - Distribution by actual outcome
    - Distribution by sensitive attribute
    """
    # This would use the raw data from results._audit.data
    # For now, showing structure
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Overall Prediction Distribution",
            "Predictions by Actual Outcome",
            "Predictions by Race",
            "Predictions by Age Group"
        )
    )
    
    # Implementation would add histograms from actual data
    # ...
    
    fig.update_layout(
        height=700,
        title_text="Model Prediction Distribution",
    )
    
    return fig


def plot_outcome_rate_comparison(results, attribute: str = "race") -> go.Figure:
    """
    Create detailed outcome rate comparison with confidence intervals.
    """
    desc = results.descriptive_stats
    
    if attribute not in desc["outcome_by_attribute"]:
        raise ValueError(f"Attribute '{attribute}' not found")
    
    attr_data = desc["outcome_by_attribute"][attribute]
    reference = attr_data["reference_group"]
    
    groups = []
    rates = []
    colors = []
    annotations = []
    
    for group, stats in attr_data["groups"].items():
        groups.append(group)
        rates.append(stats["outcome_rate"] * 100)
        
        if stats.get("is_reference"):
            colors.append("#2c3e50")
            annotations.append("REF")
        else:
            rr = stats.get("rate_ratio_vs_ref", 1.0)
            if rr > 1.25:
                colors.append("#e74c3c")  # Red - higher risk
            elif rr < 0.8:
                colors.append("#3498db")  # Blue - lower risk
            else:
                colors.append("#2ecc71")  # Green - similar
            annotations.append(f"RR: {rr:.2f}")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=groups,
        y=rates,
        marker_color=colors,
        text=[f"{r:.1f}%<br>{a}" for r, a in zip(rates, annotations)],
        textposition="outside"
    ))
    
    fig.update_layout(
        title=f"Outcome Rate by {attribute.title()} (Reference: {reference})",
        yaxis_title="Outcome Rate (%)",
        xaxis_title=attribute.title(),
        height=400
    )
    
    # Add reference line at overall rate
    overall_rate = desc["cohort_overview"]["prevalence"] * 100
    fig.add_hline(
        y=overall_rate, 
        line_dash="dash", 
        line_color="gray",
        annotation_text=f"Overall: {overall_rate:.1f}%"
    )
    
    return fig
```

### Fairness Dashboard

```python
# faircareai/visualization/fairness_dashboard.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict

def plot_dashboard_plotly(results) -> go.Figure:
    """
    Create comprehensive fairness dashboard.
    
    Layout:
    - Top left: Subgroup AUROC comparison
    - Top right: Calibration curves
    - Bottom left: Fairness metric radar
    - Bottom right: Disparity bar chart
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Subgroup Performance (AUROC)",
            "Calibration by Group",
            "Fairness Metrics",
            "Disparity from Reference"
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "scatterpolar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. Subgroup AUROC bar chart
    for attr_name, subgroups in results.subgroup_performance.items():
        groups = list(subgroups.keys())
        aurocs = [subgroups[g].get("auroc", 0) for g in groups]
        
        fig.add_trace(
            go.Bar(
                name=attr_name,
                x=groups,
                y=aurocs,
                text=[f"{a:.3f}" for a in aurocs],
                textposition="outside"
            ),
            row=1, col=1
        )
    
    # Add reference line at acceptable threshold
    fig.add_hline(
        y=results.config.thresholds.get("min_auroc", 0.65),
        line_dash="dash",
        line_color="red",
        annotation_text="Min acceptable",
        row=1, col=1
    )
    
    # 2. Placeholder for calibration (needs raw data)
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line=dict(dash="dash", color="gray"),
            name="Perfect calibration"
        ),
        row=1, col=2
    )
    
    # 3. Fairness metrics radar
    for attr_name, metrics in results.fairness_metrics.items():
        if "group_metrics" in metrics:
            for group, gm in metrics["group_metrics"].items():
                fig.add_trace(
                    go.Scatterpolar(
                        r=[gm.get("tpr", 0), gm.get("fpr", 0), 
                           gm.get("ppv", 0), gm.get("selection_rate", 0)],
                        theta=["TPR", "FPR", "PPV", "Selection Rate"],
                        fill="toself",
                        name=f"{attr_name}: {group}"
                    ),
                    row=2, col=1
                )
    
    # 4. Disparity bar chart
    for attr_name, metrics in results.fairness_metrics.items():
        if "equalized_odds_diff" in metrics:
            groups = list(metrics["equalized_odds_diff"].keys())
            diffs = list(metrics["equalized_odds_diff"].values())
            
            colors = ["red" if abs(d) > 0.1 else "green" for d in diffs]
            
            fig.add_trace(
                go.Bar(
                    name=f"{attr_name} EO Diff",
                    x=groups,
                    y=diffs,
                    marker_color=colors,
                    text=[f"{d:.3f}" for d in diffs],
                    textposition="outside"
                ),
                row=2, col=2
            )
    
    # Add threshold lines
    fig.add_hline(y=0.1, line_dash="dash", line_color="red", row=2, col=2)
    fig.add_hline(y=-0.1, line_dash="dash", line_color="red", row=2, col=2)
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text=f"FairCareAI Fairness Dashboard: {results.config.model_name}",
        showlegend=True
    )
    
    return fig


def plot_subgroup_heatmap(results, metric: str = "auroc") -> go.Figure:
    """Create heatmap of metric across all subgroups."""
    import pandas as pd
    
    # Build matrix
    data = []
    for attr_name, subgroups in results.subgroup_performance.items():
        for group, metrics in subgroups.items():
            data.append({
                "Attribute": attr_name,
                "Group": group,
                "Value": metrics.get(metric, 0),
                "N": metrics.get("n", 0)
            })
    
    df = pd.DataFrame(data)
    
    fig = px.imshow(
        df.pivot(index="Attribute", columns="Group", values="Value"),
        color_continuous_scale="RdYlGn",
        aspect="auto",
        title=f"Subgroup {metric.upper()} Heatmap"
    )
    
    # Add text annotations
    fig.update_traces(
        text=df.pivot(index="Attribute", columns="Group", values="Value").round(3),
        texttemplate="%{text}"
    )
    
    return fig
```

---

## CLI Interface

```python
# faircareai/cli.py
import click
import json
from pathlib import Path

@click.group()
@click.version_option()
def cli():
    """FairCareAI - Fairness audits for healthcare ML models."""
    pass

@cli.command()
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--pred-col", required=True, help="Prediction column name")
@click.option("--target-col", required=True, help="Target column name")
@click.option("--config", type=click.Path(exists=True), help="YAML config file")
@click.option("--output", "-o", default="fairness_report.html", help="Output path")
@click.option("--format", type=click.Choice(["html", "pdf", "json"]), default="html")
def audit(data_path, pred_col, target_col, config, output, format):
    """Run fairness audit on model predictions."""
    from faircareai import FairCareAudit
    from faircareai.core.config import FairnessConfig
    import yaml
    
    # Load config if provided
    if config:
        with open(config) as f:
            config_dict = yaml.safe_load(f)
        fc_config = FairnessConfig(**config_dict)
    else:
        fc_config = None
    
    click.echo(f"Loading data from {data_path}...")
    audit = FairCareAudit(
        data=data_path,
        pred_col=pred_col,
        target_col=target_col,
        config=fc_config
    )
    
    # Interactive attribute setup if no config
    if not config:
        click.echo("\nNo config provided. Enter sensitive attributes (empty to finish):")
        while True:
            name = click.prompt("Attribute name", default="", show_default=False)
            if not name:
                break
            reference = click.prompt(f"Reference group for {name}", default="")
            audit.add_sensitive_attribute(name=name, reference=reference or None)
    
    click.echo("\nRunning audit...")
    results = audit.run()
    
    click.echo(f"\n{results.summary()}")
    
    if format == "html":
        results.to_html(output)
    elif format == "pdf":
        results.to_pdf(output)
    else:
        results.to_json(output)
    
    click.echo(f"\nReport saved to {output}")

@cli.command()
def suggest_metric():
    """Interactive fairness metric selection guide."""
    from faircareai.fairness.decision_tree import recommend_fairness_metric, get_impossibility_warning
    from faircareai.core.config import UseCaseType
    
    click.echo(get_impossibility_warning())
    click.echo("\nSelect your use case:\n")
    
    for i, uc in enumerate(UseCaseType, 1):
        click.echo(f"  {i}. {uc.value}")
    
    choice = click.prompt("\nEnter number", type=int)
    use_case = list(UseCaseType)[choice - 1]
    
    rec = recommend_fairness_metric(use_case)
    
    click.echo(f"\n{'='*60}")
    click.echo(f"RECOMMENDED: {rec['recommended_metric']}")
    click.echo(f"{'='*60}")
    click.echo(f"\nRationale:\n{rec['rationale']}")
    
    if rec.get("alternatives"):
        click.echo(f"\nAlternatives: {', '.join(rec['alternatives'])}")
    
    if rec.get("contraindicated"):
        click.echo(f"\n⚠️  Contraindicated: {', '.join(rec['contraindicated'])}")
        click.echo(f"   Reason: {rec['contraindicated_reason']}")

if __name__ == "__main__":
    cli()
```

---

## Example YAML Config

```yaml
# faircare_config.yaml
model_name: "30-Day Readmission Risk Model"
model_version: "2.1.0"
model_type: "binary_classifier"

intended_use: "Trigger care management outreach for high-risk patients post-discharge"
intended_population: "Adult patients (18+) discharged from medicine services"
out_of_scope:
  - "Pediatric patients"
  - "Oncology discharges"
  - "Patients discharged AMA"
  - "Patients with <24 hour stays"

# REQUIRED - Fairness Configuration
primary_fairness_metric: "equalized_odds"
fairness_justification: |
  Model triggers proactive care management intervention (phone call, home visit).
  Equalizing TPR ensures all racial groups receive equal benefit from the 
  intervention when truly at risk of readmission. Equalizing FPR prevents
  unequal burden of unnecessary outreach.
use_case_type: "intervention_trigger"

# Sensitive Attributes
sensitive_attributes:
  - name: "race"
    column: "patient_race"
    reference: "White"
    categories: ["White", "Black", "Hispanic", "Asian", "Other"]
    clinical_justification: "Required for CMS health equity monitoring"
  
  - name: "sex"
    column: "patient_sex"
    reference: "Male"
  
  - name: "age_group"
    column: "age_cat"
    categories: ["18-44", "45-64", "65+"]

# Intersectional Analysis
intersections:
  - ["race", "sex"]

# Thresholds
thresholds:
  min_subgroup_n: 100
  demographic_parity_ratio: [0.8, 1.25]
  equalized_odds_diff: 0.1
  calibration_diff: 0.05
  min_auroc: 0.65
  max_missing_rate: 0.10

# Decision thresholds to evaluate
decision_thresholds: [0.3, 0.4, 0.5]

# Report Settings
organization_name: "Rush University Medical Center"
include_chai_mapping: true
```

---

## Next Steps

1. **Initialize repo**: `faircareai` on GitHub
2. **Core implementation**: Start with `config.py`, `audit.py`, `fairness.py`
3. **Test with synthetic data**: Create test fixtures
4. **Build report templates**: Jinja2 HTML/PDF
5. **PyPI release**: `pip install faircareai`

Want me to:
1. Create the initial Python files to start building?
2. Design the HTML report template with embedded Plotly?
3. Build out the metrics calculation functions?
