"""Shared fixtures for the churn predictor test suite."""
import json
import sys
from pathlib import Path

import joblib
import pytest

import matplotlib
matplotlib.use("Agg")   # headless rendering, no GUI backend in CI

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from predictor import ADDON_COLS  # noqa: E402


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def meta():
    return json.loads((ROOT / "models" / "metadata.json").read_text())


@pytest.fixture(scope="session")
def pipe():
    return joblib.load(ROOT / "models" / "model.joblib")


@pytest.fixture(scope="session")
def calibrator():
    return joblib.load(ROOT / "models" / "calibrator.joblib")


@pytest.fixture(scope="session")
def data():
    import pandas as pd
    df = pd.read_csv(ROOT / "data" / "telco_clean.csv")
    df["Total_Charges"] = pd.to_numeric(df["Total_Charges"], errors="coerce")
    return df


@pytest.fixture
def sample_row():
    """A mid-risk customer: one-year contract, fiber optic, moderate tenure."""
    return {
        "gender": "Male", "senior": "No", "partner": "No", "dependents": "No",
        "tenure": 24, "phone": "Yes", "multiple_lines": "No",
        "internet": "Fiber optic",
        "addons": {c: "No" for c in ADDON_COLS},
        "contract": "One year", "paperless": "Yes",
        "payment": "Electronic check", "monthly": 78.5,
    }
