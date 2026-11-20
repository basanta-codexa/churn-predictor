"""Individual customer churn assessment.

The prediction logic is unchanged; this page provides the Phase 1 shell
(premium light theme, professional sidebar, and reusable components).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from predictor import (ADDON_COLS, apply_calibrator, build_row,  # noqa: E402
                       driver_path, explain, feature_name_and_value,
                       score_customer)
from charts import (SHORT_VALUES, plot_drivers, plot_reliability,  # noqa: E402
                    plot_shap_waterfall)
from theme import (footer, kpi_row, note_card, panel,  # noqa: E402
                   percentile_card, risk_card, section_header)
from page_shell import setup  # noqa: E402

MODEL_PATH = ROOT / "models" / "model.joblib"
CALIBRATOR_PATH = ROOT / "models" / "calibrator.joblib"
META_PATH = ROOT / "models" / "metadata.json"


def _short(value):
    """Trim long category values so chart labels stay readable."""
    return SHORT_VALUES.get(str(value), str(value))


# --------------------------------------------------------------------------- #
# artifacts
# --------------------------------------------------------------------------- #
@st.cache_resource
def load_artifacts():
    import shap

    pipe = joblib.load(MODEL_PATH)
    calibrator = joblib.load(CALIBRATOR_PATH)
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    return pipe, calibrator, meta, explainer


pipe, calibrator, meta, explainer = load_artifacts()

if calibrator.get("method") != meta["calibration"]["method"]:
    st.error(
        "The model artifacts are inconsistent: the calibrator method does not "
        "match the metadata. Retrain the model before using the app."
    )
    st.stop()

opts = meta["cat_options"]
rng = meta["num_ranges"]
m = meta["metrics"]["test"]
cm = meta["metrics"]["confusion_matrix"]
threshold = meta["operating_point"]["threshold"]
target_recall = meta["operating_point"]["target_recall"]
base_rate = meta["calibration"]["train_base_rate"]

setup(
    page_title="Predict Churn",
    eyebrow="Predict churn",
    title="Customer churn risk",
    subtitle=(
        "Estimate the probability that a customer will churn and review the "
        "factors driving the score."
    ),
    meta=[
        f"Model <b>{meta['model']['name']}</b>",
        f"<b>{meta['data']['rows_modeling']:,}</b> customers",
        f"<b>{len(meta['feature_order'])}</b> features",
        f"Trained <b>{meta['trained_at'][:10]}</b>",
    ],
)

st.markdown(
    kpi_row([
        (f"{m['roc_auc']:.3f}", "ROC-AUC",
         f"CV {meta['metrics']['cv']['roc_auc_mean']:.3f}"),
        (f"{m['recall']:.0%}", "Recall", "churners identified"),
        (f"{m['precision']:.0%}", "Precision", "of flagged customers"),
        (f"{m['pr_auc']:.2f}", "PR-AUC", f"base rate {base_rate:.2f}"),
        (f"{base_rate:.0%}", "Churn rate", "training population"),
    ]),
    unsafe_allow_html=True,
)
st.caption(
    "Metrics are computed once on the held-out test set. The threshold is "
    f"selected on training data for at least {target_recall:.0%} recall."
)

# --------------------------------------------------------------------------- #
# customer inputs
# --------------------------------------------------------------------------- #
st.sidebar.header("Customer inputs")
st.sidebar.caption(
    "Options and numeric bounds are taken from the training data. The "
    "assessment updates as inputs change."
)

tenure_range = rng["Tenure_Months"]
monthly_range = rng["Monthly_Charges"]
total_range = rng["Total_Charges"]

st.sidebar.subheader("A. Customer profile")
tenure = st.sidebar.slider(
    "Tenure (months)", int(tenure_range["min"]), int(tenure_range["max"]),
    int(tenure_range["median"]))
gender = st.sidebar.selectbox("Gender", opts["Gender"])
senior = st.sidebar.selectbox("Senior citizen", opts["Senior_Citizen"])
partner = st.sidebar.selectbox("Partner", opts["Partner"])
dependents = st.sidebar.selectbox("Dependents", opts["Dependents"])

st.sidebar.subheader("B. Subscription information")
contract = st.sidebar.selectbox("Contract", opts["Contract"])
phone = st.sidebar.selectbox("Phone service", opts["Phone_Service"])
if phone == "No":
    multiple_lines = "No phone service"
else:
    line_options = [value for value in opts["Multiple_Lines"]
                    if value != "No phone service"] or ["No", "Yes"]
    multiple_lines = st.sidebar.selectbox("Multiple lines", line_options)

internet = st.sidebar.selectbox("Internet service", opts["Internet_Service"])
addons = {}
for col in ADDON_COLS:
    if internet == "No":
        addons[col] = "No internet service"
    else:
        addon_options = [value for value in opts[col]
                         if value != "No internet service"] or ["No", "Yes"]
        addons[col] = st.sidebar.selectbox(
            col.replace("_", " "), addon_options)

st.sidebar.subheader("C. Billing information")
payment = st.sidebar.selectbox("Payment method", opts["Payment_Method"])
monthly = st.sidebar.slider(
    "Monthly charges ($)", float(monthly_range["min"]),
    float(monthly_range["max"]), float(monthly_range["median"]), step=0.5)

estimate = tenure * monthly
use_estimate = st.sidebar.checkbox(
    "Estimate total charges", value=True,
    help="Total charges are estimated as tenure multiplied by monthly charges. "
         "Untick to enter the actual lifetime value.")
if use_estimate:
    total = estimate
    st.sidebar.caption(f"Estimated total charges: ${estimate:,.0f}")
    if not total_range["min"] <= estimate <= total_range["max"]:
        st.sidebar.warning(
            "The estimate falls outside the training range. Enter the actual "
            "total charges for a more reliable score."
        )
else:
    total = st.sidebar.number_input(
        "Total charges ($)", min_value=0.0,
        max_value=float(total_range["max"]), value=float(estimate), step=10.0)

paperless = st.sidebar.selectbox(
    "Paperless billing", opts["Paperless_Billing"])

st.sidebar.button("Predict Churn", type="primary")

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
model_prediction = ("Will churn" if probability >= threshold
                    else "Will stay")

explanation = explain(explainer, pipe, meta, result["X_new"])
short_names, values = feature_name_and_value(explanation["names"], row)

path = driver_path(
    explanation["feature_phi"], explanation["base_value"],
    transform=lambda p: apply_calibrator(
        calibrator["estimator"], calibrator["method"], p),
)
base_p = path["base_p"]

# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
st.markdown(
    section_header("Assessment", "Calibrated risk for this customer"),
    unsafe_allow_html=True,
)

head1, head2, head3 = st.columns([1, 1, 1.15], gap="medium")

with head1:
    st.markdown(
        risk_card(probability, band["label"], band["color"], percentile,
                  threshold, base_p),
        unsafe_allow_html=True,
    )

with head2:
    st.markdown(
        percentile_card(percentile, threshold, probability, target_recall),
        unsafe_allow_html=True,
    )

with head3:
    st.markdown(
        note_card(
            "Interpretation",
            "This probability is a model estimate, not a guaranteed outcome. "
            f"Model prediction: <strong>{model_prediction}</strong> at the "
            f"{threshold:.0%} operating threshold. A score of 30% means that "
            "roughly 30 in 100 comparable customers churned.",
            note=f"Calibrated on out-of-fold training predictions · "
                 f"{cm['tp']} churners identified, {cm['fn']} missed, "
                 f"{cm['fp']} non-churners flagged.",
        ),
        unsafe_allow_html=True,
    )


def _display_value(name, value):
    if name in ("Monthly_Charges", "Total_Charges"):
        return f"${value:,.2f}"
    if name == "Tenure_Months":
        return f"{value:g} months"
    return str(value)


attribute_names = ["Tenure_Months", "Contract", "Internet_Service",
                   "Payment_Method", "Monthly_Charges", "Total_Charges"]
attribute_html = "".join(
    f"<li><strong>{name.replace('_', ' ')}</strong>: "
    f"{_display_value(name, row[name])}</li>"
    for name in attribute_names)
st.markdown(
    panel(
        "Customer attributes used",
        f'<ul class="planned-list">{attribute_html}</ul>',
        caption="Exact values passed to the model for this assessment.",
        phase="This prediction",
    ),
    unsafe_allow_html=True,
)

with st.expander("Model performance (held-out test set)"):
    st.markdown(
        f"""
| Metric | Value |
|---|---:|
| ROC-AUC | {m['roc_auc']:.3f} |
| PR-AUC | {m['pr_auc']:.3f} |
| Precision | {m['precision']:.3f} |
| Recall | {m['recall']:.3f} |
| F1 | {m['f1']:.3f} |
| Brier score | {m['brier']:.3f} |
| Log loss | {m['log_loss']:.3f} |
| Cross-validated ROC-AUC | {meta['metrics']['cv']['roc_auc_mean']:.3f} ± {meta['metrics']['cv']['roc_auc_std']:.3f} |
"""
    )
    st.caption(
        f"Model: {meta['model']['name']}, selected on "
        f"{meta['selection']['cv_folds']}-fold stratified cross-validation "
        "over the training split only."
    )

# --------------------------------------------------------------------------- #
# explanation
# --------------------------------------------------------------------------- #
st.markdown(
    section_header("Risk drivers", "SHAP-based explanation of this score"),
    unsafe_allow_html=True,
)

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
    f"Red bars increase churn risk; blue bars reduce it. The path starts at "
    f"the model baseline of {path['base_p']:.0%} and ends at this "
    f"customer's score of {path['final_p']:.0%}. Total charges were entered as "
    f"${total:,.0f}"
    + (" (estimated as tenure multiplied by monthly charges)."
       if use_estimate else ".")
)

with st.expander("SHAP attribution (log-odds)"):
    order = np.argsort(-np.abs(explanation["feature_phi"]))[:12]
    shap_labels = [f"{short_names[i]} = {_short(values[i])}" for i in order]
    st.plotly_chart(
        plot_shap_waterfall(shap_labels, explanation["feature_phi"][order],
                            explanation["base_value"]),
        width="stretch", theme=None, config={"displayModeBar": False})
    st.caption(
        "SHAP values are additive in log-odds. One-hot columns are summed back "
        "into their original feature, so there is one bar per feature rather "
        f"than one per encoded column. The base value is "
        f"{explanation['base_value']:.3f}."
    )

with st.expander("Calibration"):
    st.plotly_chart(plot_reliability(meta["calibration_curve"]),
                    width="stretch", theme=None,
                    config={"displayModeBar": False})
    cal = meta["calibration"]
    st.caption(
        f"Calibration method: {cal['method']}, selected by cross-validated log "
        f"loss. Mean predicted probability on the training set is "
        f"{cal['mean_calibrated_score_train']:.1%} against a base rate of "
        f"{cal['train_base_rate']:.1%}."
    )

with st.expander("Limitations and intended use"):
    st.markdown(
        "- The model is trained on the public IBM Telco sample and has not "
        "been validated on external data.\n"
        "- The dataset has no time dimension, so the model cannot capture "
        "behavioural drift.\n"
        "- SHAP values describe associations in the model, not causal effects. "
        "Retention actions should be validated experimentally.\n"
        "- Total charges are estimated as tenure multiplied by monthly "
        "charges unless the actual value is entered; this can change the score "
        "for a small number of customers.\n"
        "- This application is a demonstration, not a production decision "
        "system."
    )

st.markdown(
    footer([
        ("Model", meta["model"]["name"]),
        ("Test ROC-AUC", f"{m['roc_auc']:.3f}"),
        ("Dataset", f"{meta['data']['rows_modeling']:,} customers"),
        ("Trained", meta["trained_at"][:10]),
    ]),
    unsafe_allow_html=True,
)
