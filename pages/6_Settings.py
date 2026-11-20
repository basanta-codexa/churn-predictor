"""Application and model configuration (read-only in this demo)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from theme import footer, panel, section_header  # noqa: E402
from page_shell import setup  # noqa: E402

META_PATH = ROOT / "models" / "metadata.json"
MODELING_PATH = ROOT / "data" / "telco_modeling.csv"

meta = json.loads(META_PATH.read_text(encoding="utf-8"))

setup(
    page_title="Settings",
    eyebrow="Settings",
    title="Settings",
    subtitle="Application, model, and classification configuration.",
    meta=[
        "Version <b>1.0</b>",
        f"Model <b>{meta['model']['name']}</b>",
        f"Schema <b>v{meta['schema_version']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.caption(
    "Configuration is read-only in this demonstration. Changing model or "
    "threshold settings requires a validated retraining and deployment step."
)

st.markdown(
    section_header("Application", "Version and runtime information"),
    unsafe_allow_html=True,
)
versions = meta["library_versions"]
app_html = (
    "<ul class='planned-list'>"
    "<li><strong>Application:</strong> Retention Intelligence v1.0</li>"
    f"<li><strong>Metadata schema:</strong> v{meta['schema_version']}</li>"
    f"<li><strong>Python:</strong> {versions.get('python', 'unknown')}</li>"
    f"<li><strong>scikit-learn:</strong> "
    f"{versions.get('scikit-learn', 'unknown')}</li>"
    f"<li><strong>XGBoost:</strong> {versions.get('xgboost', 'unknown')}</li>"
    f"<li><strong>Trained at:</strong> {meta['trained_at']}</li>"
    f"<li><strong>Source commit:</strong> "
    f"{meta.get('git_commit', 'unknown')}</li>"
    "</ul>"
)
st.markdown(
    panel("Runtime", app_html, phase="Read-only"),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Model and risk configuration",
                   "Values stored with the committed artifacts"),
    unsafe_allow_html=True,
)
operation = meta["operating_point"]
bands = meta["risk_bands"]
risk_html = (
    "<ul class='planned-list'>"
    f"<li><strong>Model:</strong> {meta['model']['name']}</li>"
    f"<li><strong>Calibration:</strong> {meta['calibration']['method']}</li>"
    f"<li><strong>Operating threshold:</strong> "
    f"{operation['threshold']:.4f} (target recall "
    f"{operation['target_recall']:.0%})</li>"
    f"<li><strong>High risk:</strong> "
    f"percentile ≥ {bands['high']['min_percentile']:.0f}</li>"
    f"<li><strong>Medium risk:</strong> "
    f"percentile ≥ {bands['medium']['min_percentile']:.0f}</li>"
    f"<li><strong>Low risk:</strong> below the operating threshold</li>"
    "</ul>"
)
st.markdown(
    panel("Classification rules", risk_html, phase="Read-only"),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Data export", "Committed files available for download"),
    unsafe_allow_html=True,
)
export_col, _, _ = st.columns([1.4, 1, 1])
with export_col:
    st.download_button(
        "Download metadata.json",
        data=META_PATH.read_bytes(),
        file_name="metadata.json",
        mime="application/json",
    )
    st.download_button(
        "Download telco_modeling.csv",
        data=MODELING_PATH.read_bytes(),
        file_name="telco_modeling.csv",
        mime="text/csv",
    )

st.markdown(
    footer([
        ("Application", "Retention Intelligence v1.0"),
        ("Model", meta["model"]["name"]),
        ("Schema", f"v{meta['schema_version']}"),
    ]),
    unsafe_allow_html=True,
)
