"""Business overview and model snapshot."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from theme import footer, kpi_row, panel, section_header  # noqa: E402
from page_shell import setup  # noqa: E402

meta = json.loads((ROOT / "models" / "metadata.json").read_text(encoding="utf-8"))
m = meta["metrics"]["test"]
base_rate = meta["calibration"]["train_base_rate"]

setup(
    page_title="Overview",
    eyebrow="Overview",
    title="Retention intelligence",
    subtitle="Business health and churn analytics for the current model.",
    meta=[
        f"<b>{meta['data']['rows_modeling']:,}</b> customers",
        f"<b>{base_rate:.0%}</b> churn rate",
        f"Model <b>{meta['model']['name']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    kpi_row([
        (f"{meta['data']['rows_modeling']:,}", "Customers", "modelling dataset"),
        (f"{base_rate:.0%}", "Churn rate", "training population"),
        (f"{m['roc_auc']:.3f}", "Test ROC-AUC", "held-out split"),
        (f"{m['recall']:.0%}", "Recall", "churners identified"),
        (f"{m['precision']:.0%}", "Precision", "of flagged customers"),
    ]),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Business health", "Churn analytics planned for Phase 2"),
    unsafe_allow_html=True,
)

st.markdown(
    panel(
        "Churn risk distribution",
        "<p>Segment the customer base by calibrated churn probability and "
        "show how many customers fall into each risk band.</p>",
        caption="Distribution of churn risk across the customer base.",
        phase="Phase 2",
    ),
    unsafe_allow_html=True,
)
st.markdown(
    panel(
        "Customer segmentation",
        "<p>Break down churn by contract, internet service, payment method, "
        "tenure, and add-on services.</p>",
        caption="Descriptive segmentation of the customer population.",
        phase="Phase 2",
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
        ("Dataset", f"{meta['data']['rows_modeling']:,} customers"),
        ("Trained", meta["trained_at"][:10]),
    ]),
    unsafe_allow_html=True,
)
