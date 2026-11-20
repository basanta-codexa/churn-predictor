"""Risk segmentation and retention guidance."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from charts import plot_risk_distribution  # noqa: E402
from data_loader import load_scored_frame  # noqa: E402
from theme import footer, kpi_row, panel, section_header  # noqa: E402
from page_shell import setup  # noqa: E402


@st.cache_data(show_spinner="Scoring customers...")
def get_scored_data():
    return load_scored_frame()


frame, meta = get_scored_data()
counts = frame["risk_band"].value_counts().reindex(
    ["low", "medium", "high"], fill_value=0)
total = len(frame)

setup(
    page_title="Retention Insights",
    eyebrow="Retention Insights",
    title="Retention insights",
    subtitle="Risk drivers and retention strategies grounded in model output.",
    meta=[
        f"<b>{counts['high']:,}</b> high risk",
        f"<b>{counts['medium']:,}</b> medium risk",
        f"Model <b>{meta['model']['name']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    kpi_row([
        (f"{counts['high']:,}", "High risk",
         f"{counts['high'] / total:.1%} of customers"),
        (f"{counts['medium']:,}", "Medium risk",
         f"{counts['medium'] / total:.1%} of customers"),
        (f"{counts['low']:,}", "Low risk",
         f"{counts['low'] / total:.1%} of customers"),
        (f"{frame['churn_probability'].mean():.1%}", "Average risk",
         "calibrated mean"),
    ]),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Customer risk segmentation",
                   "Calibrated risk bands from the committed model"),
    unsafe_allow_html=True,
)
st.plotly_chart(
    plot_risk_distribution(counts),
    width="stretch", theme=None, config={"displayModeBar": False})

st.caption(
    "Risk bands combine the calibrated probability threshold with the "
    "training-population percentile bands stored in model metadata."
)

high_risk = (frame[frame["risk_band"] == "high"]
             .nlargest(10, "churn_probability")
             [["CustomerID", "churn_probability", "Tenure_Months",
               "Contract", "Monthly_Charges"]]
             .copy())
high_risk["churn_probability"] = high_risk[
    "churn_probability"].map(lambda value: f"{value:.1%}")
high_risk["Monthly_Charges"] = high_risk[
    "Monthly_Charges"].map(lambda value: f"${value:,.2f}")
st.dataframe(high_risk, hide_index=True, width="stretch")
st.caption("Ten highest-risk customers from the committed dataset.")

st.markdown(
    panel(
        "Churn drivers",
        "<p>Aggregated SHAP attributions and retention guidance are added "
        "in the next step.</p>",
        caption="Model associations, not proven causes.",
        phase="Next step",
    ),
    unsafe_allow_html=True,
)

st.markdown(
    footer([
        ("Application", "Retention Intelligence"),
        ("Dataset", f"{total:,} customers"),
        ("Model", meta["model"]["name"]),
    ]),
    unsafe_allow_html=True,
)
