"""Business overview and model snapshot."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from charts import (plot_category_churn, plot_churn_outcome,  # noqa: E402
                    plot_probability_distribution, plot_risk_distribution,
                    plot_tenure_churn)
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
threshold = meta["operating_point"]["threshold"]


def category_summary(column):
    summary = (frame.groupby(column)["Churn_Value"]
               .agg(["mean", "size"])
               .reset_index())
    summary.columns = ["category", "churn_rate", "count"]
    return summary.sort_values("churn_rate", ascending=False)


contract_summary = category_summary("Contract")
payment_summary = category_summary("Payment_Method")

tenure_bins = [0, 12, 24, 36, 48, 60, 72]
tenure_labels = ["0-12", "13-24", "25-36", "37-48", "49-60", "61-72"]
frame["_tenure_group"] = pd.cut(
    frame["Tenure_Months"], bins=tenure_bins, labels=tenure_labels,
    include_lowest=True)
tenure_summary = (frame.groupby("_tenure_group", observed=True)["Churn_Value"]
                  .agg(["mean", "size"])
                  .reset_index())
tenure_summary.columns = ["tenure_group", "churn_rate", "count"]

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

st.plotly_chart(
    plot_churn_outcome(frame["Churn_Value"].value_counts()),
    width="stretch", theme=None, config={"displayModeBar": False})

left, right = st.columns(2, gap="medium")
with left:
    st.plotly_chart(
        plot_category_churn(contract_summary, "Churn by contract type"),
        width="stretch", theme=None, config={"displayModeBar": False})
with right:
    st.plotly_chart(
        plot_category_churn(payment_summary, "Churn by payment method"),
        width="stretch", theme=None, config={"displayModeBar": False})

st.plotly_chart(
    plot_tenure_churn(tenure_summary),
    width="stretch", theme=None, config={"displayModeBar": False})
st.plotly_chart(
    plot_probability_distribution(frame["churn_probability"], threshold),
    width="stretch", theme=None, config={"displayModeBar": False})

st.caption(
    "All charts use the committed dataset and calibrated model scores. "
    "Churn rates are observed outcomes, not model estimates."
)

st.markdown(
    section_header("Customer risk overview",
                   "Highest-risk customers by calibrated probability"),
    unsafe_allow_html=True,
)

top_customers = (frame
                 .nlargest(10, "churn_probability")
                 [["CustomerID", "churn_probability", "risk_band_label",
                   "Tenure_Months", "Contract", "Monthly_Charges"]]
                 .copy())
top_customers["churn_probability"] = top_customers[
    "churn_probability"].map(lambda value: f"{value:.1%}")
top_customers["Monthly_Charges"] = top_customers[
    "Monthly_Charges"].map(lambda value: f"${value:,.2f}")
st.dataframe(top_customers, hide_index=True, width="stretch")
st.caption(
    "Customer IDs are taken from the committed raw dataset. The table shows "
    "the ten highest calibrated probabilities. Open Predict Churn from the "
    "sidebar for a detailed customer assessment."
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
