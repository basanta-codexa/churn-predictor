"""Business overview and model snapshot."""
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
m = meta["metrics"]["test"]
base_rate = meta["calibration"]["train_base_rate"]

counts = frame["risk_band"].value_counts().reindex(
    ["low", "medium", "high"], fill_value=0)
high_risk = int(counts["high"])
churn_rate = float(frame["Churn_Value"].mean())
avg_probability = float(frame["churn_probability"].mean())

setup(
    page_title="Overview",
    eyebrow="Overview",
    title="Customer intelligence",
    subtitle=("Monitor customer health, identify churn risks, and discover "
              "retention opportunities."),
    meta=[
        f"<b>{len(frame):,}</b> customers",
        f"<b>{churn_rate:.1%}</b> observed churn",
        f"Model <b>{meta['model']['name']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    kpi_row([
        (f"{len(frame):,}", "Total customers", "modelling dataset"),
        (f"{churn_rate:.1%}", "Churn rate", "observed in dataset"),
        (f"{high_risk:,}", "High-risk customers", "top risk band"),
        (f"{avg_probability:.1%}", "Avg churn probability", "calibrated mean"),
    ]),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Business health", "Churn analytics from the committed data"),
    unsafe_allow_html=True,
)

st.plotly_chart(
    plot_risk_distribution(counts),
    width="stretch", theme=None, config={"displayModeBar": False})

st.caption(
    "Risk bands use the committed percentile bands and the operating "
    "threshold selected on the training split."
)

st.markdown(
    panel(
        "Customer segmentation",
        "<p>Break down churn by contract, internet service, payment method, "
        "tenure, and add-on services.</p>",
        caption="Descriptive segmentation of the customer population.",
        phase="Next step",
    ),
    unsafe_allow_html=True,
)

st.markdown(
    panel(
        "Model performance overview",
        f"<p>Test ROC-AUC <strong>{m['roc_auc']:.3f}</strong>, PR-AUC "
        f"<strong>{m['pr_auc']:.3f}</strong>, recall "
        f"<strong>{m['recall']:.0%}</strong>, and precision "
        f"<strong>{m['precision']:.0%}</strong>.</p>",
        caption="The current held-out metrics from metadata.",
        phase="Available now",
    ),
    unsafe_allow_html=True,
)

st.markdown(
    footer([
        ("Application", "Retention Intelligence"),
        ("Model", meta["model"]["name"]),
        ("Dataset", f"{len(frame):,} customers"),
        ("Trained", meta["trained_at"][:10]),
    ]),
    unsafe_allow_html=True,
)
