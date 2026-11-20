"""Customer directory with search, filters, ranking and pagination."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_scored_frame  # noqa: E402
from theme import footer, section_header  # noqa: E402
from page_shell import setup  # noqa: E402


@st.cache_data(show_spinner="Scoring customers...")
def get_scored_data():
    return load_scored_frame()


frame, meta = get_scored_data()

setup(
    page_title="Customer Intelligence",
    eyebrow="Customer Intelligence",
    title="Customer intelligence",
    subtitle="Explore customers, segments, and their calibrated churn risk.",
    meta=[
        f"<b>{len(frame):,}</b> customers",
        f"<b>{frame['risk_band'].eq('high').sum():,}</b> high risk",
        f"Model <b>{meta['model']['name']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    section_header("Customer directory",
                   "Search, filter and rank customers by churn probability"),
    unsafe_allow_html=True,
)

search_col, risk_col, contract_col = st.columns([2, 1, 1.5])
search = search_col.text_input("Search customer ID", placeholder="e.g. 3668-QPYBK")
risk_order = ["high", "medium", "low"]
risk_filter = risk_col.multiselect("Risk band", risk_order, default=risk_order)
contract_options = sorted(frame["Contract"].unique().tolist())
contract_filter = contract_col.multiselect(
    "Contract", contract_options, default=contract_options)

filtered = frame[
    frame["risk_band"].isin(risk_filter)
    & frame["Contract"].isin(contract_filter)
]
if search.strip():
    filtered = filtered[
        filtered["CustomerID"].str.contains(search.strip(), case=False,
                                            na=False)]

filtered = filtered.sort_values("churn_probability", ascending=False)

rows_per_page = st.selectbox("Rows per page", [25, 50, 100], index=1)
pages = max(1, math.ceil(len(filtered) / rows_per_page))
page_number = st.number_input("Page", min_value=1, max_value=pages, value=1)
start = (page_number - 1) * rows_per_page
page_frame = filtered.iloc[start:start + rows_per_page].copy()

page_frame["churn_probability"] = page_frame[
    "churn_probability"].map(lambda value: f"{value:.1%}")
page_frame["Monthly_Charges"] = page_frame[
    "Monthly_Charges"].map(lambda value: f"${value:,.2f}")

display_columns = ["CustomerID", "churn_probability", "risk_band_label",
                   "Tenure_Months", "Contract", "Monthly_Charges"]
st.dataframe(
    page_frame[display_columns], hide_index=True, width="stretch")
st.caption(
    f"Showing {len(page_frame):,} of {len(filtered):,} matching customers "
    f"(page {page_number} of {pages}). Probabilities are calibrated model "
    "scores, not certain outcomes."
)

st.markdown(
    footer([
        ("Application", "Retention Intelligence"),
        ("Dataset", f"{len(frame):,} customers"),
        ("Model", meta["model"]["name"]),
    ]),
    unsafe_allow_html=True,
)
