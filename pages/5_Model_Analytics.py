"""Model performance and explainability."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import streamlit as st
from sklearn.metrics import (average_precision_score, precision_recall_curve,
                             roc_curve)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from charts import (plot_confusion_matrix, plot_global_drivers,  # noqa: E402
                    plot_pr_curve, plot_reliability, plot_roc_curve)
from data_loader import (MODEL_PATH, load_scored_frame,  # noqa: E402
                         test_split_indices)
from explainability import global_driver_summary  # noqa: E402
from theme import footer, kpi_row, panel, section_header  # noqa: E402
from page_shell import setup  # noqa: E402


@st.cache_data(show_spinner="Scoring customers...")
def get_scored_data():
    return load_scored_frame()


@st.cache_resource
def get_explainer():
    pipe = joblib.load(MODEL_PATH)
    import shap
    return pipe, shap.TreeExplainer(pipe.named_steps["model"])


@st.cache_data(show_spinner="Aggregating SHAP values...")
def get_driver_summary(data, metadata):
    pipe, explainer = get_explainer()
    return global_driver_summary(data, metadata, pipe, explainer)


frame, meta = get_scored_data()
m = meta["metrics"]["test"]

test_indices = test_split_indices(frame)
y_test = frame.iloc[test_indices]["Churn_Value"].to_numpy()
test_raw = frame.iloc[test_indices]["raw_score"].to_numpy()
test_prob = frame.iloc[test_indices]["churn_probability"].to_numpy()

fpr, tpr, _ = roc_curve(y_test, test_raw)
precision, recall, _ = precision_recall_curve(y_test, test_prob)
average_precision = average_precision_score(y_test, test_prob)
baseline = float(y_test.mean())

setup(
    page_title="Model Analytics",
    eyebrow="Model Analytics",
    title="Model analytics",
    subtitle="Performance and explainability of the committed model.",
    meta=[
        f"Model <b>{meta['model']['name']}</b>",
        f"Test ROC-AUC <b>{m['roc_auc']:.3f}</b>",
        f"Calibration <b>{meta['calibration']['method']}</b>",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    kpi_row([
        (f"{m['roc_auc']:.3f}", "ROC-AUC", "held-out test"),
        (f"{m['pr_auc']:.3f}", "PR-AUC", f"baseline {baseline:.2f}"),
        (f"{m['precision']:.0%}", "Precision", "at operating threshold"),
        (f"{m['recall']:.0%}", "Recall", "at operating threshold"),
        (f"{m['brier']:.3f}", "Brier score", "lower is better"),
    ]),
    unsafe_allow_html=True,
)

st.markdown(
    section_header("Performance", "All figures use the held-out test split"),
    unsafe_allow_html=True,
)

roc_col, pr_col = st.columns(2, gap="medium")
with roc_col:
    st.plotly_chart(
        plot_roc_curve(fpr, tpr, m["roc_auc"]),
        width="stretch", theme=None, config={"displayModeBar": False})
with pr_col:
    st.plotly_chart(
        plot_pr_curve(recall, precision, average_precision, baseline),
        width="stretch", theme=None, config={"displayModeBar": False})

cm_col, cal_col = st.columns(2, gap="medium")
with cm_col:
    st.plotly_chart(
        plot_confusion_matrix(meta["metrics"]["confusion_matrix"]),
        width="stretch", theme=None, config={"displayModeBar": False})
with cal_col:
    st.plotly_chart(
        plot_reliability(meta["calibration_curve"]),
        width="stretch", theme=None, config={"displayModeBar": False})

st.metric(
    "Log loss", f"{m['log_loss']:.3f}",
    help="Computed on held-out predictions with probabilities clipped away "
         "from 0 and 1.")

st.markdown(
    section_header("Feature importance",
                   "Average SHAP impact on the model's raw output"),
    unsafe_allow_html=True,
)
driver_summary = get_driver_summary(frame, meta)
st.plotly_chart(
    plot_global_drivers(driver_summary),
    width="stretch", theme=None, config={"displayModeBar": False})

params = meta["model"]["params"]
model_html = (
    "<ul class='planned-list'>"
    f"<li><strong>Model type:</strong> {meta['model']['name']}</li>"
    f"<li><strong>Parameters:</strong> "
    f"{json.dumps(params, sort_keys=True)}</li>"
    f"<li><strong>Encoded features:</strong> "
    f"{meta['model']['encoded_feature_count']}</li>"
    f"<li><strong>Training rows:</strong> "
    f"{meta['model']['n_training_rows']:,}</li>"
    f"<li><strong>Test rows:</strong> "
    f"{meta['model']['n_test_rows']:,}</li>"
    f"<li><strong>Calibration:</strong> {meta['calibration']['method']} "
    f"(CV log loss {meta['calibration']['cv_log_loss'][meta['calibration']['method']]:.3f})</li>"
    f"<li><strong>Cross-validated ROC-AUC:</strong> "
    f"{meta['metrics']['cv']['roc_auc_mean']:.3f} ± "
    f"{meta['metrics']['cv']['roc_auc_std']:.3f}</li>"
    f"<li><strong>Trained:</strong> {meta['trained_at'][:10]} "
    f"(commit {meta.get('git_commit', 'unknown')})</li>"
    "</ul>"
)
st.markdown(
    panel("Model information", model_html,
          caption="Stored metadata; test metrics are not production performance.",
          phase="Committed artifacts"),
    unsafe_allow_html=True,
)

st.markdown(
    footer([
        ("Application", "Retention Intelligence"),
        ("Model", meta["model"]["name"]),
        ("Test ROC-AUC", f"{m['roc_auc']:.3f}"),
    ]),
    unsafe_allow_html=True,
)
