"""Shared data access for the analytics pages.

The module rebuilds the modelling frame from the committed raw dataset so a
real ``CustomerID`` can be carried through to the analytics views. Scoring uses
the committed pipeline and calibrator only; no metrics or customer records are
invented.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from predictor import apply_calibrator, band_for

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "telco_churn.csv"
MODEL_PATH = ROOT / "models" / "model.joblib"
CALIBRATOR_PATH = ROOT / "models" / "calibrator.joblib"
META_PATH = ROOT / "models" / "metadata.json"

TARGET = "Churn_Value"

#: Columns present in the raw file but deliberately excluded from modelling.
DROP_COLS = [
    "CustomerID", "Count", "Country", "State", "City", "Zip_Code",
    "Lat_Long", "Latitude", "Longitude", "Churn_Label", "Churn_Score",
    "CLTV", "Churn_Reason",
]


def load_meta():
    return json.loads(META_PATH.read_text(encoding="utf-8"))


def load_model_frame(meta):
    """Return the deduplicated modelling frame with its original CustomerID."""
    raw = pd.read_csv(RAW_PATH)
    raw.columns = raw.columns.str.strip().str.replace(" ", "_")
    raw["Total_Charges"] = pd.to_numeric(raw["Total_Charges"], errors="coerce")

    feature_cols = list(meta["feature_order"])
    key_cols = feature_cols + [TARGET]

    ids = (raw[["CustomerID"] + key_cols]
           .drop_duplicates(subset=key_cols)["CustomerID"]
           .reset_index(drop=True))

    frame = (raw.drop(columns=DROP_COLS)
             .drop_duplicates()
             .reset_index(drop=True))
    frame.insert(0, "CustomerID", ids)
    return frame


def _percentiles(raw_scores, quantiles):
    q = np.asarray(quantiles, dtype=float)
    if q.size < 2:
        return np.full(len(raw_scores), 50.0)
    positions = np.searchsorted(q, np.asarray(raw_scores, dtype=float),
                                side="right")
    return np.clip(positions / (q.size - 1) * 100.0, 0.0, 100.0)


def load_scored_frame():
    """Score every modelling customer and attach calibrated risk fields."""
    meta = load_meta()
    frame = load_model_frame(meta)

    pipe = joblib.load(MODEL_PATH)
    calibrator = joblib.load(CALIBRATOR_PATH)

    raw_scores = pipe.predict_proba(frame[meta["feature_order"]])[:, 1]
    probabilities = apply_calibrator(
        calibrator["estimator"], calibrator["method"], raw_scores)
    percentiles = _percentiles(
        raw_scores, meta["score_reference"]["quantiles"])

    threshold = meta["operating_point"]["threshold"]
    bands = [
        band_for(float(percentile), meta["risk_bands"], float(probability),
                 threshold)
        for percentile, probability in zip(percentiles, probabilities)
    ]

    frame["raw_score"] = raw_scores
    frame["churn_probability"] = probabilities
    frame["percentile"] = percentiles
    frame["risk_band"] = [band["name"] for band in bands]
    frame["risk_band_label"] = [band["label"] for band in bands]
    frame["risk_band_color"] = [band["color"] for band in bands]
    return frame, meta
