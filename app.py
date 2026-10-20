"""Streamlit app for the customer churn predictor.

Run with:  streamlit run app.py

The app shows three things for a single customer:

* a **calibrated churn probability** (the raw model output is a ranking
  score; ``models/calibrator.joblib`` maps it onto a real probability),
* where that customer sits in the **population** (percentile and risk band),
* **why** the model scored them that way (SHAP, aggregated back to the 19
  raw features and shown in probability points).

All form options, slider bounds and reported metrics come from
``models/metadata.json``, so the app follows the data instead of hardcoding
numbers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from predictor import (ADDON_COLS, apply_calibrator, build_row,  # noqa: E402
                       driver_path, explain, feature_name_and_value,
                       score_customer)
from charts import (SHORT_VALUES, plot_drivers, plot_reliability,  # noqa: E402
                    plot_shap_waterfall)
from theme import (CSS, footer, hero, kpi_row, note_card,  # noqa: E402
                   percentile_card, risk_card)

MODEL_PATH = ROOT / "models" / "model.joblib"
CALIBRATOR_PATH = ROOT / "models" / "calibrator.joblib"
META_PATH = ROOT / "models" / "metadata.json"

st.set_page_config(page_title="Churn Predictor", page_icon="📉", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def _short(value):
    """Trim long category values so the chart labels stay readable."""
    return SHORT_VALUES.get(str(value), str(value))


# --------------------------------------------------------------------------- #
# artifacts
# --------------------------------------------------------------------------- #
@st.cache_resource
def load_artifacts():
    import shap
    pipe = joblib.load(MODEL_PATH)
    calibrator = joblib.load(CALIBRATOR_PATH)
    meta = json.loads(META_PATH.read_text())
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    return pipe, calibrator, meta, explainer


pipe, calibrator, meta, explainer = load_artifacts()
opts = meta["cat_options"]
rng = meta["num_ranges"]


# --------------------------------------------------------------------------- #
# inputs
# --------------------------------------------------------------------------- #
st.markdown(
    hero(
        badge=f"{meta['model']['name']} + SHAP &nbsp;·&nbsp; calibrated risk",
        title="Customer Churn Predictor",
        subtitle=(
            "Predict which telecom customers are about to leave - and see "
            "exactly which factors pushed them there."
        ),
        chips=[
            f"<b>{meta['data']['rows_modeling']:,}</b> customers",
            f"<b>{len(meta['feature_order'])}</b> features",
            f"<b>{meta['metrics']['test']['roc_auc']}</b> ROC-AUC",
            f"<b>{meta['metrics']['test']['recall']:.0%}</b> recall",
            f"<b>{meta['calibration']['method']}</b> calibrated",
        ],
    ),
    unsafe_allow_html=True,
)

m = meta["metrics"]["test"]
cm = meta["metrics"]["confusion_matrix"]
st.markdown(
    kpi_row([
        (f"{m['roc_auc']:.3f}", "ROC-AUC", f"CV {meta['metrics']['cv']['roc_auc_mean']:.3f}"),
        (f"{m['recall']:.0%}", "Recall", "churners caught"),
        (f"{m['precision']:.0%}", "Precision", "of those contacted"),
        (f"{m['pr_auc']:.2f}", "PR-AUC", "vs 0.27 base rate"),
        (f"{meta['calibration']['train_base_rate']:.0%}", "Churn rate", "of the population"),
    ]),
    unsafe_allow_html=True,
)

st.sidebar.header("Customer details")

st.sidebar.subheader("Account")
tenure_range = rng["Tenure_Months"]
monthly_range = rng["Monthly_Charges"]
total_range = rng["Total_Charges"]

tenure = st.sidebar.slider(
    "Tenure (months)", int(tenure_range["min"]), int(tenure_range["max"]),
    int(tenure_range["median"]))
monthly = st.sidebar.slider(
    "Monthly charges ($)", float(monthly_range["min"]), float(monthly_range["max"]),
    float(monthly_range["median"]), step=0.5)
contract = st.sidebar.selectbox("Contract", opts["Contract"])
paperless = st.sidebar.selectbox("Paperless billing", opts["Paperless_Billing"])
payment = st.sidebar.selectbox("Payment method", opts["Payment_Method"])

estimate = tenure * monthly
use_estimate = st.sidebar.checkbox(
    "Estimate total charges", value=True,
    help=f"Total charges are what the customer has paid over their lifetime. "
         f"Currently estimated at ${estimate:,.0f} (tenure x monthly charges). "
         f"Untick to enter the real value.")
if use_estimate:
    total = estimate
    st.sidebar.caption(f"Total charges estimated at ${estimate:,.0f}")
else:
    total = st.sidebar.number_input(
        "Total charges ($)", min_value=0.0, max_value=float(total_range["max"]),
        value=float(estimate), step=10.0)

st.sidebar.subheader("Demographics")
gender = st.sidebar.selectbox("Gender", opts["Gender"])
senior = st.sidebar.selectbox("Senior citizen", opts["Senior_Citizen"])
partner = st.sidebar.selectbox("Partner", opts["Partner"])
dependents = st.sidebar.selectbox("Dependents", opts["Dependents"])

st.sidebar.subheader("Services")
phone = st.sidebar.selectbox("Phone service", opts["Phone_Service"])
if phone == "No":
    multiple_lines = "No phone service"
else:
    multiple_lines = st.sidebar.selectbox("Multiple lines", ["No", "Yes"])

internet = st.sidebar.selectbox("Internet service", opts["Internet_Service"])
addons = {}
for col in ADDON_COLS:
    if internet == "No":
        addons[col] = "No internet service"
    else:
        addons[col] = st.sidebar.selectbox(col.replace("_", " "), ["No", "Yes"])

st.sidebar.caption(
    "Slider bounds come from the training data, so the model is never asked "
    "to extrapolate beyond the population it was trained on."
)

# --------------------------------------------------------------------------- #
# predict
# --------------------------------------------------------------------------- #
row = build_row(
    gender=gender, senior=senior, partner=partner, dependents=dependents,
    tenure=tenure, phone=phone, multiple_lines=multiple_lines,
    internet=internet, addons=addons, contract=contract,
    paperless=paperless, payment=payment, monthly=monthly,
    total_charges=total,
)

result = score_customer(pipe, calibrator["estimator"], meta, row)
probability = result["churn_probability"]
percentile = result["percentile"]
band = result["band"]
threshold = meta["operating_point"]["threshold"]

# The explanation and the driver path are needed by both the summary cards
# and the chart, so they are computed once here.
explanation = explain(explainer, pipe, meta, result["X_new"])
short_names, values = feature_name_and_value(explanation["names"], row)

path = driver_path(
    explanation["feature_phi"], explanation["base_value"],
    transform=lambda p: apply_calibrator(calibrator["estimator"],
                                         calibrator["method"], p),
)
base_p = path["base_p"]

# --------------------------------------------------------------------------- #
# prediction summary - a full width strip, so the chart below gets the room
# it needs for its labels at every screen size
# --------------------------------------------------------------------------- #
st.markdown("### Prediction")

head1, head2, head3 = st.columns([1, 1, 1.15], gap="medium")

with head1:
    st.markdown(
        risk_card(probability, band["label"], band["color"], percentile,
                  threshold, base_p),
        unsafe_allow_html=True,
    )

with head2:
    st.markdown(
        percentile_card(percentile, threshold, probability),
        unsafe_allow_html=True,
    )

with head3:
    st.markdown(
        note_card(
            "About this number",
            "The model is class weighted to favour recall, so its raw output "
            "is a ranking score. A calibrator fitted on out-of-fold "
            "predictions turns it into the probability shown here - the "
            "average predicted risk matches the churn rate almost exactly.",
            note=f"Threshold {threshold:.0%} · {cm['tp']} churners caught, "
                 f"{cm['fn']} missed, {cm['fp']} loyal customers contacted.",
        ),
        unsafe_allow_html=True,
    )

with st.expander("Model performance (test set)"):
    st.markdown(
        f"- ROC-AUC: **{m['roc_auc']}**\n"
        f"- PR-AUC: **{m['pr_auc']}**\n"
        f"- Precision: **{m['precision']}**\n"
        f"- Recall: **{m['recall']}**\n"
        f"- F1: **{m['f1']}**\n"
        f"- Brier score: **{m['brier']}** (lower is better)\n"
        f"- Cross-validated ROC-AUC: "
        f"**{meta['metrics']['cv']['roc_auc_mean']}** "
        f"(+/- {meta['metrics']['cv']['roc_auc_std']})"
    )
    st.caption(
        f"Model: {meta['model']['name']}, selected on "
        f"{meta['selection']['cv_folds']}-fold cross-validation over the "
        "training split only."
    )

# --------------------------------------------------------------------------- #
# explain
# --------------------------------------------------------------------------- #
st.markdown("### Why this prediction?")

segment_labels, segment_names, segment_values = [], [], []
for indices, _ in path["segments"]:
    if len(indices) == 1:
        i = indices[0]
        segment_labels.append(f"{short_names[i]} = {_short(values[i])}")
        segment_names.append(short_names[i])
        segment_values.append(values[i])
    else:
        segment_labels.append(f"Other factors ({len(indices)})")
        segment_names.append("Other factors")
        segment_values.append(f"{len(indices)} features")

st.plotly_chart(
    plot_drivers(segment_labels, path["steps"], path["base_p"],
                 path["final_p"], name=segment_names, value=segment_values),
    width="stretch", theme=None, config={"displayModeBar": False})
st.caption(
    f"Red pushes the customer toward churn, blue away. Bars are the change "
    f"in churn probability when that factor is applied on top of the ones "
    f"above it (ordered by impact), starting from the population average of "
    f"{path['base_p']:.0%} and ending at {path['final_p']:.0%}. "
    f"Hover a bar for the exact numbers. "
    f"Total charges were entered as ${total:,.0f}"
    + (" (estimated as tenure x monthly charges)." if use_estimate else ".")
)

with st.expander("SHAP detail (log-odds, exact additive attribution)"):
    order = np.argsort(-np.abs(explanation["feature_phi"]))[:12]
    shap_labels = [f"{short_names[i]} = {_short(values[i])}" for i in order]
    st.plotly_chart(
        plot_shap_waterfall(shap_labels, explanation["feature_phi"][order],
                            explanation["base_value"]),
        width="stretch", theme=None, config={"displayModeBar": False})
    st.caption(
        "SHAP values are additive in log-odds: every bar is the effect of that "
        "feature on the model's raw output, and the bars add up exactly to the "
        f"model score (E[f(X)] = {explanation['base_value']:.3f} plus the bars "
        "gives f(x)). The chart above converts them into probability points. "
        "One-hot columns are summed back into their original feature, so there "
        "is one bar per feature rather than one per dummy column."
    )

with st.expander("How well calibrated is the model?"):
    st.plotly_chart(plot_reliability(meta["calibration_curve"]),
                    width="stretch", theme=None,
                    config={"displayModeBar": False})
    cal = meta["calibration"]
    st.caption(
        f"Calibration method: **{cal['method']}** "
        f"(chosen by cross-validated log loss against isotonic). "
        f"Mean predicted probability on the training set is "
        f"{cal['mean_calibrated_score_train']:.1%} against a base rate of "
        f"{cal['train_base_rate']:.1%}."
    )

st.markdown(
    footer([
        ("Model", meta["model"]["name"]),
        ("Dataset", f"{meta['data']['rows_modeling']:,} customers"),
        ("Features", f"{len(meta['feature_order'])}"),
        ("Trained", meta["trained_at"][:10]),
    ]),
    unsafe_allow_html=True,
)
