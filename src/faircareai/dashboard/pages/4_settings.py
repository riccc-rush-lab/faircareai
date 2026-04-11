"""
FairCareAI - Settings Page

Configuration and preferences for the dashboard.
All settings are stored in session state and read by other pages.
"""

import streamlit as st

from faircareai.dashboard.components.accessibility import (
    render_semantic_heading,
    render_skip_link,
)
from faircareai.dashboard.components.audience_toggle import (
    get_audience_mode,
    set_audience_mode,
)
from faircareai.visualization.themes import GOVERNANCE_DISCLAIMER_SHORT


def render_settings_page() -> None:
    """Render the settings page."""
    render_skip_link()

    render_semantic_heading("Settings", level=1, id="page-title")
    st.caption(f"Step 4 of 4 | {GOVERNANCE_DISCLAIMER_SHORT}")

    st.markdown("---")

    # Display Preferences
    render_semantic_heading("Display Preferences", level=2, id="display")

    col1, col2 = st.columns(2)

    with col1:
        # Default audience mode
        current_mode = get_audience_mode()
        new_mode = st.selectbox(
            "Default View Mode",
            options=["governance", "data_scientist"],
            format_func=lambda x: "Governance Committee" if x == "governance" else "Data Scientist",
            index=0 if current_mode == "governance" else 1,
            help="Choose the default level of technical detail",
        )
        if new_mode != current_mode:
            set_audience_mode(new_mode)

    with col2:
        # Color theme (functional: stored in session state)
        st.selectbox(
            "Color Theme",
            options=["Default (Okabe-Ito)", "High Contrast"],
            help="Okabe-Ito palette is colorblind-safe",
            key="color_theme",
        )

    # Analysis defaults
    st.markdown("---")
    render_semantic_heading("Analysis Defaults", level=2, id="analysis")

    st.markdown(
        "These settings are used as defaults on the Analysis page. "
        "You can override them per-session on the Analysis sidebar."
    )

    col1, col2 = st.columns(2)

    with col1:
        def _sync_threshold() -> None:
            """Clear analysis slider key so it picks up the new default."""
            st.session_state.pop("analysis_threshold", None)

        st.slider(
            "Default Decision Threshold",
            0.0,
            1.0,
            0.5,
            0.01,
            help="Default threshold for binary classification",
            key="default_threshold",
            on_change=_sync_threshold,
        )

        st.slider(
            "Disparity Threshold",
            0.0,
            0.3,
            0.1,
            0.01,
            help="Threshold for flagging metric disparities between groups",
            key="disparity_threshold",
        )

    with col2:
        st.number_input(
            "Minimum Sample Size Warning",
            min_value=10,
            max_value=500,
            value=50,
            help="Groups below this size will show warnings",
            key="min_sample_warning",
        )

        st.number_input(
            "Bootstrap Iterations",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100,
            help="Number of bootstrap iterations for confidence intervals",
            key="bootstrap_iterations",
        )

    # Fairness configuration
    st.markdown("---")
    render_semantic_heading("Fairness Configuration", level=2, id="fairness")

    st.markdown("""
    Configure which fairness metrics to prioritize and their thresholds.
    These settings follow responsible AI governance standards and can be adjusted based on clinical context.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Primary Fairness Metric",
            options=[
                "Equalized Odds",
                "Equal Opportunity",
                "Demographic Parity",
                "Predictive Parity",
                "Calibration",
            ],
            help="Main metric for fairness evaluation",
            key="primary_fairness_metric",
        )

    with col2:
        st.text_input(
            "Fairness Justification",
            placeholder="e.g., Equal opportunity prioritized due to high-stakes clinical context",
            help="Document rationale for fairness metric selection",
            key="fairness_justification",
        )

    # Report configuration
    st.markdown("---")
    render_semantic_heading("Report Configuration", level=2, id="reports")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Organization Name",
            placeholder="Acme Health System",
            help="Appears on generated reports",
            key="org_name",
        )

        st.text_input(
            "Model Name",
            placeholder="ICU Mortality Prediction v2.1",
            help="Name of the model being audited",
            key="model_name",
        )

    with col2:
        st.text_input(
            "Contact Email",
            placeholder="ai-governance@hospital.org",
            help="Contact for governance inquiries",
            key="contact_email",
        )

        st.text_area(
            "Report Footer",
            placeholder="Custom footer text for generated reports",
            help="Additional text to include in reports",
            key="report_footer",
        )

    # Data management
    st.markdown("---")
    render_semantic_heading("Data Management", level=2, id="data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Uploaded Data", type="secondary", use_container_width=True):
            for key in ["uploaded_data", "audit_result", "data_source", "data_validated",
                        "selected_demographic_cols", "audit_threshold",
                        "target_col", "pred_col"]:
                st.session_state.pop(key, None)
            st.success("Uploaded data cleared")
            st.rerun()

    with col2:
        if st.button("Reset All Settings", type="secondary", use_container_width=True):
            # Keep only essential session state
            keys_to_keep = {"audience_mode"}
            keys_to_delete = [k for k in st.session_state.keys() if k not in keys_to_keep]
            for k in keys_to_delete:
                del st.session_state[k]
            st.success("Settings reset to defaults")
            st.rerun()

    # About section
    st.markdown("---")
    render_semantic_heading("About FairCareAI", level=2, id="about")

    from faircareai import __version__

    st.markdown(f"""
    **FairCareAI** is an open-source toolkit for algorithmic fairness auditing
    in healthcare AI systems. It implements responsible AI governance principles
    and transparent reporting standards for predictive models.

    ### Key Features
    - WCAG 2.1 AA compliant interface
    - Dual-audience design (Data Scientists + Governance Committees)
    - Publication-ready data visualization
    - Comprehensive fairness metrics
    - Governance sign-off workflow

    ### Resources
    - [GitHub Repository](https://github.com/riccc-rush-lab/faircareai)
    - [CHAI Framework](https://www.coalitionforhealthai.org)

    ### Version
    FairCareAI v{__version__}
    """)

    # Navigation
    st.markdown("---")
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("pages/1_upload.py")


# Run the page
render_settings_page()
