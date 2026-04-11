"""
FairCareAI - Data Upload Page

Handles data upload with column mapping, validation, and preview.
Supports CSV and Parquet files.
WCAG 2.1 AA compliant with clear error messaging.
"""

from decimal import Decimal

import polars as pl
import streamlit as st

from faircareai.dashboard.components.accessibility import (
    announce_status_change,
    render_semantic_heading,
    render_skip_link,
)
from faircareai.dashboard.components.audience_toggle import (
    render_audience_toggle,
)
from faircareai.visualization.themes import GOVERNANCE_DISCLAIMER_SHORT


def validate_mapped_data(
    df: pl.DataFrame,
    target_col: str,
    pred_col: str,
) -> tuple[bool, list[str]]:
    """Validate uploaded DataFrame using user-selected column mappings.

    Args:
        df: Uploaded DataFrame.
        target_col: User-selected outcome column.
        pred_col: User-selected prediction column.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []

    # Check outcome column is binary
    unique_values = df[target_col].unique().to_list()
    if not set(unique_values).issubset({0, 1}):
        errors.append(
            f"Column `{target_col}` must be binary (0/1). "
            f"Found {len(unique_values)} unique values: {unique_values[:10]}"
        )

    # Check prediction column is numeric and in [0, 1]
    pred_data = df[pred_col]
    dtype_str = str(pred_data.dtype).lower()

    if "int" in dtype_str and set(pred_data.unique().to_list()).issubset({0, 1}):
        # Binary predictions — acceptable
        pass
    elif "int" in dtype_str or "float" in dtype_str:
        min_val_raw = pred_data.min()
        max_val_raw = pred_data.max()
        min_val = float(min_val_raw) if isinstance(min_val_raw, int | float | Decimal) else None
        max_val = float(max_val_raw) if isinstance(max_val_raw, int | float | Decimal) else None

        if min_val is None or max_val is None:
            errors.append(
                f"Column `{pred_col}` must be numeric and contain at least one non-null value."
            )
        elif min_val < 0 or max_val > 1:
            errors.append(
                f"Column `{pred_col}` should be in range [0, 1]. "
                f"Found range: [{min_val:.4f}, {max_val:.4f}]. "
                "If these are logits, apply sigmoid: 1 / (1 + exp(-x))."
            )
    else:
        errors.append(
            f"Column `{pred_col}` must be numeric (int or float). Found type: {pred_data.dtype}"
        )

    return len(errors) == 0, errors


def detect_demographic_columns(df: pl.DataFrame, exclude: set[str]) -> list[dict]:
    """Detect potential demographic columns with metadata.

    Args:
        df: DataFrame to analyze.
        exclude: Column names to exclude (target, prediction).

    Returns:
        List of column info dictionaries.
    """
    columns = []

    for col in df.columns:
        if col in exclude:
            continue

        col_data = df[col]
        n_unique = col_data.n_unique()
        dtype = str(col_data.dtype)

        # Categorize column type
        if n_unique <= 20:
            col_type = "categorical"
            sample_values = col_data.unique().to_list()[:5]
        elif "int" in dtype.lower() or "float" in dtype.lower():
            col_type = "numeric"
            sample_values = [f"min: {str(col_data.min())}", f"max: {str(col_data.max())}"]
        else:
            col_type = "text"
            sample_values = col_data.head(3).to_list()

        # Check for likely demographic indicators
        demographic_keywords = [
            "race",
            "ethnicity",
            "gender",
            "sex",
            "age",
            "insurance",
            "language",
            "income",
            "education",
            "zip",
            "region",
            "site",
        ]
        is_likely_demo = any(kw in col.lower() for kw in demographic_keywords)

        columns.append(
            {
                "name": col,
                "type": col_type,
                "n_unique": n_unique,
                "sample_values": sample_values,
                "is_likely_demographic": is_likely_demo,
                "null_count": col_data.null_count(),
            }
        )

    return columns


def render_upload_page() -> None:
    """Render the data upload page."""
    render_skip_link()

    render_semantic_heading("Data Upload", level=1, id="page-title")

    st.caption(f"Step 1 of 4 | {GOVERNANCE_DISCLAIMER_SHORT}")

    # Audience toggle
    st.markdown("---")
    audience = render_audience_toggle()
    st.markdown("---")

    # Instructions based on audience
    if audience == "governance":
        st.markdown("""
        ### Upload Your Model's Predictions

        To analyze your AI model for fairness, we need a file containing:

        1. **Patient outcomes** - What actually happened (any column name)
        2. **Model predictions** - What the model predicted (any column name)
        3. **Patient demographics** - Groups to compare (e.g., race, insurance, age)

        Your data scientist can prepare this file for you.
        """)
    else:
        st.markdown("""
        ### Data Requirements

        Upload a CSV or Parquet file with the following:

        | Required | Type | Description |
        |----------|------|-------------|
        | Outcome column | Binary (0/1) | Ground truth outcome |
        | Prediction column | Float [0,1] or Binary | Predicted probability or binary prediction |
        | Demographic columns | Any | One or more demographic attributes |

        **Notes:**
        - Column names are flexible — you'll map them in the next step
        - Minimum recommended sample size: 500 per group
        - All rows should be from the same evaluation cohort
        """)

    # Demo data option
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Parquet file",
            type=["csv", "parquet"],
            help="Upload a file with patient outcomes, model predictions, and demographics",
        )

    with col2:
        st.markdown("#### Or Try Demo Data")
        if st.button(
            "Load Demo Dataset",
            type="secondary",
            use_container_width=True,
            help="Load synthetic ICU mortality prediction data for demonstration",
        ):
            from faircareai.data.synthetic import generate_icu_mortality_data

            demo_df = generate_icu_mortality_data(n_samples=2000, seed=42)
            st.session_state["uploaded_data"] = demo_df
            st.session_state["data_source"] = "demo"
            announce_status_change("Demo dataset loaded successfully")
            st.success("Demo dataset loaded. Configure column mapping below.")

    # Process uploaded file
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".parquet"):
                df = pl.read_parquet(uploaded_file)
            else:
                df = pl.read_csv(uploaded_file)
            st.session_state["uploaded_data"] = df
            st.session_state["data_source"] = "uploaded"
            announce_status_change("File uploaded successfully")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            announce_status_change("Error reading uploaded file", priority="assertive")
            return

    # Show data preview, column mapping, and validation
    if "uploaded_data" in st.session_state:
        df = st.session_state["uploaded_data"]

        st.markdown("---")
        render_semantic_heading("Data Preview", level=2)

        # Basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("File Type", st.session_state.get("data_source", "unknown").title())

        # Data preview
        with st.expander("View First 10 Rows", expanded=True):
            st.dataframe(df.head(10).to_pandas(), use_container_width=True)

        # --- Column Mapping ---
        st.markdown("---")
        render_semantic_heading("Column Mapping", level=2)

        if audience == "governance":
            st.markdown(
                "Select which columns contain the patient outcomes and model predictions. "
                "We'll try to detect these automatically."
            )
        else:
            st.markdown(
                "Map your columns to FairCareAI's expected roles. "
                "Any column name works — no renaming needed."
            )

        all_cols = df.columns

        # Smart defaults: try to detect outcome and prediction columns
        target_default = 0
        pred_default = 0
        for i, col in enumerate(all_cols):
            col_lower = col.lower()
            if col_lower in {"y_true", "outcome", "mortality", "label", "target", "event"}:
                target_default = i
            if col_lower in {"y_prob", "y_pred", "prediction", "risk_score", "prob", "score"}:
                pred_default = i

        col1, col2 = st.columns(2)
        with col1:
            target_col = st.selectbox(
                "Outcome column (binary 0/1)",
                options=all_cols,
                index=target_default,
                help="Column with actual patient outcomes (0 = no event, 1 = event)",
                key="target_col_select",
            )
        with col2:
            pred_col = st.selectbox(
                "Prediction column (probabilities or binary)",
                options=all_cols,
                index=pred_default,
                help="Column with model predictions (probabilities [0,1] or binary 0/1)",
                key="pred_col_select",
            )

        # Show outcome prevalence if target column is valid
        if target_col:
            try:
                unique_vals = set(df[target_col].unique().to_list())
                if unique_vals.issubset({0, 1}):
                    prevalence = df[target_col].mean()
                    st.caption(f"Outcome prevalence in `{target_col}`: {prevalence:.1%}")
            except Exception:
                pass

        # Store column mapping in session state
        st.session_state["target_col"] = target_col
        st.session_state["pred_col"] = pred_col

        # --- Validation ---
        st.markdown("---")
        render_semantic_heading("Validation", level=2)

        if target_col == pred_col:
            st.error("Outcome and prediction columns must be different.")
            announce_status_change(
                "Validation error: same column selected twice", priority="assertive"
            )
            return

        is_valid, errors = validate_mapped_data(df, target_col, pred_col)

        if is_valid:
            st.success("Data validation passed.")
            announce_status_change("Data validation passed")
        else:
            st.error("Data validation failed. Please fix the following issues:")
            for error in errors:
                st.markdown(f"- {error}")
            announce_status_change("Data validation failed", priority="assertive")

        # --- Demographic Column Selection ---
        if is_valid:
            st.markdown("---")
            render_semantic_heading("Select Demographic Columns", level=2)

            if audience == "governance":
                st.markdown("""
                Select which columns represent patient groups you want to analyze for fairness.
                We've highlighted columns that look like demographic attributes.
                """)
            else:
                st.markdown("""
                Select protected attributes for fairness analysis.
                Columns with low cardinality (20 unique values) work best.
                """)

            exclude_cols = {target_col, pred_col}
            detected_cols = detect_demographic_columns(df, exclude_cols)

            # Group by type - select likely demographic columns
            likely_demo = [c for c in detected_cols if c["is_likely_demographic"]]
            default_selections = [c["name"] for c in likely_demo]

            selected_cols = st.multiselect(
                "Demographic columns to analyze",
                options=[c["name"] for c in detected_cols],
                default=default_selections[:3],  # Limit default to 3
                help="Select columns representing patient demographic groups",
            )

            # Show column details
            if selected_cols:
                with st.expander("Selected Column Details", expanded=False):
                    for col_info in detected_cols:
                        if col_info["name"] in selected_cols:
                            st.markdown(f"**{col_info['name']}**")
                            st.markdown(f"- Type: {col_info['type']}")
                            st.markdown(f"- Unique values: {col_info['n_unique']}")
                            st.markdown(f"- Sample: {col_info['sample_values']}")
                            if col_info["null_count"] > 0:
                                st.warning(f"- Missing values: {col_info['null_count']:,}")
                            st.markdown("---")

            st.session_state["selected_demographic_cols"] = selected_cols

            # --- Prepare normalized data for analysis ---
            # Rename user columns to standard names so analysis page works generically
            st.markdown("---")
            if selected_cols:
                if st.button(
                    "Continue to Analysis",
                    type="primary",
                    use_container_width=True,
                ):
                    # Build a normalized DataFrame with standard column names.
                    # Drop any existing y_true/y_prob/y_pred columns that would
                    # collide with the renamed columns (only if they're not the
                    # columns the user actually selected).
                    std_names = {"y_true", "y_prob", "y_pred"}
                    user_cols = {target_col, pred_col}
                    collisions = (std_names - user_cols) & set(df.columns)
                    normalized_df = df.drop(list(collisions)) if collisions else df

                    rename_map = {}
                    if target_col != "y_true":
                        rename_map[target_col] = "y_true"
                    if pred_col != "y_prob" and pred_col != "y_pred":
                        # Determine if it's probabilities or binary
                        unique_vals = set(normalized_df[pred_col].unique().to_list())
                        if unique_vals.issubset({0, 1}):
                            rename_map[pred_col] = "y_pred"
                        else:
                            rename_map[pred_col] = "y_prob"

                    if rename_map:
                        normalized_df = normalized_df.rename(rename_map)
                    else:
                        normalized_df = normalized_df

                    st.session_state["uploaded_data"] = normalized_df
                    st.session_state["data_validated"] = True
                    st.switch_page("pages/2_analysis.py")
            else:
                st.warning("Please select at least one demographic column to continue.")


# Run the page
render_upload_page()
