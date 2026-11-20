"""Core prediction logic for the churn app.

Kept deliberately free of Streamlit so that it can be unit tested (see
``tests/``) and reused from notebooks.

Responsibilities
----------------
* build a feature row from the raw customer inputs in the app form
* score it with the trained pipeline and the fitted calibrator
* translate the score into a population percentile and a risk band
* aggregate SHAP values from the 46 encoded columns back to the 19 raw features

The model itself is a tree ensemble, so its raw output is a *ranking score*,
not a probability: the training used class weighting to favour recall. The
calibrator (see ``src/train.py``) maps that score onto the real churn
probability, and every number the app shows goes through it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

EPS = 1e-6

#: Feature columns that the app asks the user about, in display order.
INPUT_FEATURES = [
    "Gender", "Senior_Citizen", "Partner", "Dependents", "Tenure_Months",
    "Phone_Service", "Multiple_Lines", "Internet_Service", "Online_Security",
    "Online_Backup", "Device_Protection", "Tech_Support", "Streaming_TV",
    "Streaming_Movies", "Contract", "Paperless_Billing", "Payment_Method",
    "Monthly_Charges", "Total_Charges",
]

#: Add-on services that only exist when the customer has internet.
ADDON_COLS = [
    "Online_Security", "Online_Backup", "Device_Protection",
    "Tech_Support", "Streaming_TV", "Streaming_Movies",
]


# --------------------------------------------------------------------------- #
# small maths helpers
# --------------------------------------------------------------------------- #
def logit(p):
    """Log-odds of a probability, numerically safe at the edges."""
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    """Logistic function."""
    return 1.0 / (1.0 + np.exp(-np.asarray(z, dtype=float)))


# --------------------------------------------------------------------------- #
# feature construction
# --------------------------------------------------------------------------- #
def build_row(gender, senior, partner, dependents, tenure, phone, multiple_lines,
              internet, addons, contract, paperless, payment, monthly,
              total_charges=None):
    """Build the 19-column feature dictionary the model expects.

    ``addons`` is a mapping of the six add-on services to ``Yes``/``No``;
    the ``No internet service`` / ``No phone service`` sentinels are applied
    here so that the values always match how they appear in the training data.
    """
    tenure = float(tenure)
    monthly = float(monthly)

    if total_charges is None:
        total = tenure * monthly
    else:
        total = float(total_charges)

    if phone == "No":
        multiple_lines = "No phone service"

    if internet == "No":
        addons = {col: "No internet service" for col in ADDON_COLS}

    row = {
        "Gender": gender,
        "Senior_Citizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "Tenure_Months": tenure,
        "Phone_Service": phone,
        "Multiple_Lines": multiple_lines,
        "Internet_Service": internet,
        **addons,
        "Contract": contract,
        "Paperless_Billing": paperless,
        "Payment_Method": payment,
        "Monthly_Charges": monthly,
        "Total_Charges": total,
    }
    missing = set(INPUT_FEATURES) - set(row)
    if missing:
        raise ValueError(f"missing features in row: {sorted(missing)}")
    return row


def to_frame(row, meta):
    """Turn a feature dict into a one-row DataFrame with the training column order."""
    return pd.DataFrame([row])[meta["feature_order"]]


# --------------------------------------------------------------------------- #
# calibration
# --------------------------------------------------------------------------- #
def apply_calibrator(calibrator, method, p):
    """Map raw model scores onto calibrated churn probabilities.

    ``isotonic`` uses a fitted :class:`sklearn.isotonic.IsotonicRegression`,
    ``sigmoid`` uses a :class:`sklearn.linear_model.LogisticRegression` fitted
    on the log-odds of the raw score.
    """
    p = np.asarray(p, dtype=float)
    if method == "isotonic":
        return np.asarray(calibrator.predict(p), dtype=float)
    if method == "sigmoid":
        z = logit(p).reshape(-1, 1)
        return calibrator.predict_proba(z)[:, 1]
    raise ValueError(f"unknown calibration method: {method!r}")


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def percentile_of(score, quantiles):
    """Population percentile of ``score`` given the reference quantiles.

    ``quantiles`` are the training-set score quantiles at levels 0.00 .. 1.00.
    """
    q = np.asarray(quantiles, dtype=float)
    if q.size == 0:
        return 50.0
    pct = np.searchsorted(q, float(score), side="right") / (q.size - 1) * 100.0
    return float(np.clip(pct, 0.0, 100.0))


def band_for(percentile, risk_bands, probability=None, threshold=None):
    """Pick the risk band for a customer.

    When the calibrated ``probability`` and the operating ``threshold`` are
    supplied, the band is anchored to that threshold so the two verdicts the
    app shows can never disagree:

    * below the threshold -> ``low`` (no outreach),
    * at or above the threshold -> ``medium`` or ``high`` (outreach).

    Within the actionable group, ``high`` is the top slice of the training
    population (``min_percentile``) and ``medium`` is the rest. Bands are
    defined on percentiles rather than raw scores so they keep their meaning
    whatever the score distribution looks like.

    The percentile-only fallback is kept for callers that do not have a
    calibrated probability (e.g. exploratory notebooks).
    """
    low = dict(risk_bands.get("low", {}), name="low")

    if probability is not None and threshold is not None:
        if probability < threshold:
            return low
        high = risk_bands.get("high")
        if high is not None and percentile >= high["min_percentile"]:
            return dict(high, name="high")
        medium = risk_bands.get("medium")
        if medium is not None:
            return dict(medium, name="medium")
        return low

    for name in ("high", "medium", "low"):
        band = risk_bands.get(name)
        if band is None:
            continue
        if percentile >= band["min_percentile"]:
            return dict(band, name=name)
    return low


def score_customer(pipe, calibrator, meta, row):
    """Score one customer and return every number the app displays."""
    X_new = to_frame(row, meta)
    raw = float(pipe.predict_proba(X_new)[0, 1])
    probability = float(apply_calibrator(calibrator, meta["calibration"]["method"], [raw])[0])
    percentile = percentile_of(raw, meta["score_reference"]["quantiles"])
    band = band_for(percentile, meta["risk_bands"], probability,
                    meta["operating_point"]["threshold"])
    return {
        "X_new": X_new,
        "raw_score": raw,
        "churn_probability": probability,
        "percentile": percentile,
        "band": band,
    }


# --------------------------------------------------------------------------- #
# SHAP
# --------------------------------------------------------------------------- #
def feature_groups(prep, meta):
    """Map each raw feature to the encoded columns it produced.

    Returns a list of ``(feature_name, [column indices])`` pairs. The numeric
    block comes first in the transformed matrix, then the one-hot block, one
    contiguous run per categorical feature.
    """
    cat_transformer = prep.named_transformers_["cat"]
    ohe = (cat_transformer.named_steps["onehot"]
           if hasattr(cat_transformer, "named_steps") else cat_transformer)
    out_idx = prep.output_indices_
    num_start = out_idx["num"].start
    cat_start = out_idx["cat"].start

    groups = []
    for j, col in enumerate(meta["num_cols"]):
        groups.append((col, [num_start + j]))
    pos = cat_start
    for col, cats in zip(meta["cat_cols"], ohe.categories_):
        groups.append((col, list(range(pos, pos + len(cats)))))
        pos += len(cats)
    return groups


def explain(explainer, pipe, meta, X_new):
    """Explain a single prediction, aggregated back to the raw features.

    SHAP values are additive in log-odds. Summing the one-hot columns that
    belong to the same raw feature turns 46 numbers into 19, each one the
    effect of that feature as a whole.

    The returned ``feature_phi`` is ordered like ``meta["feature_order"]`` -
    the same order as ``names`` - so it can be indexed by feature name
    without any further bookkeeping.
    """
    prep = pipe.named_steps["prep"]
    Xt = prep.transform(X_new)
    if hasattr(Xt, "toarray"):
        Xt = Xt.toarray()
    names_out = list(prep.get_feature_names_out())
    explanation = explainer(pd.DataFrame(Xt, columns=names_out))

    phi = np.asarray(explanation.values)[0]
    base = float(np.asarray(explanation.base_values).ravel()[0])

    groups = feature_groups(prep, meta)
    phi_by_name = {name: float(phi[idx].sum()) for name, idx in groups}
    order = meta["feature_order"]
    missing = [name for name in order if name not in phi_by_name]
    if missing:
        raise ValueError(f"features missing from the SHAP grouping: {missing}")
    feature_phi = np.array([phi_by_name[name] for name in order], dtype=float)

    return {
        "base_value": base,
        "feature_phi": feature_phi,
        "phi_by_name": phi_by_name,
        "groups": groups,
        "names": list(order),
        "explanation": explanation,
    }


def driver_path(feature_phi, base_value, transform=None, top_n=10):
    """Turn additive log-odds SHAP values into a probability path.

    The features are ordered by absolute impact and applied one after the
    other; the probability is recomputed after every step, so the resulting
    bar sizes telescope exactly from the population baseline to the final
    probability of this customer. Features below ``top_n`` are folded into a
    single "other factors" bar so that the path always ends on the exact
    score the app shows.

    ``transform`` maps raw model probabilities onto calibrated ones, which
    keeps the chart consistent with the headline number in the app.
    """
    transform = transform or (lambda p: np.asarray(p, dtype=float))
    order = np.argsort(-np.abs(feature_phi))
    head, tail = order[:top_n], order[top_n:]

    segments = [(np.array([i]), float(feature_phi[i])) for i in head]
    if tail.size:
        segments.append((tail, float(feature_phi[tail].sum())))

    cumulative = base_value
    path_points = []
    for _, phi_sum in segments:
        cumulative += phi_sum
        path_points.append(float(sigmoid(cumulative)))
    path = np.asarray(transform(path_points), dtype=float)
    base_p = float(np.asarray(transform([float(sigmoid(base_value))])).ravel()[0])
    steps = np.diff(np.concatenate([[base_p], path]))
    return {
        "segments": segments,
        "order": head,
        "tail": tail,
        "path": path,
        "steps": steps,
        "base_p": base_p,
        "final_p": float(path[-1]),
    }


def feature_name_and_value(names, row):
    """Split each feature into a short display name and the selected value.

    Returns ``(short_names, values)``, e.g. ``(["Contract"], ["Month-to-month"])``.
    """
    short_names, values = [], []
    for name in names:
        value = row.get(name)
        if name == "Tenure_Months":
            short_names.append("Tenure")
            values.append(f"{value:g} months")
        elif name == "Monthly_Charges":
            short_names.append("Monthly charges")
            values.append(f"${value:,.2f}")
        elif name == "Total_Charges":
            short_names.append("Total charges")
            values.append(f"${value:,.2f}")
        else:
            short_names.append(name.replace("_", " "))
            values.append(str(value))
    return short_names, values


def feature_labels(names, row):
    """Human readable labels, e.g. ``Contract = Month-to-month``."""
    short_names, values = feature_name_and_value(names, row)
    return [f"{short} = {value}" for short, value in zip(short_names, values)]
