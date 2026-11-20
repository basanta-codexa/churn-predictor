"""Smoke tests for the churn predictor.

They cover the things that would silently break the app: a missing or
mismatched artifact, a feature added to the data but not to the form, a
calibrator that is no longer monotone, or a SHAP aggregation that no longer
adds up.
"""
import json
import math
import re

import numpy as np
import pandas as pd
import pytest

from predictor import (ADDON_COLS, INPUT_FEATURES, apply_calibrator, band_for,
                       build_row, driver_path, explain, feature_labels,
                       feature_name_and_value, percentile_of, score_customer,
                       to_frame)


# --------------------------------------------------------------------------- #
# artifacts
# --------------------------------------------------------------------------- #
def test_artifacts_exist(root):
    for name in ("model.joblib", "calibrator.joblib", "metadata.json"):
        assert (root / "models" / name).is_file(), f"missing artifact {name}"


def test_pipeline_is_a_two_step_pipeline(pipe):
    assert list(pipe.named_steps) == ["prep", "model"]
    assert pipe.named_steps["prep"].output_indices_ is not None


def test_metadata_is_complete(meta):
    for key in ("feature_order", "num_cols", "cat_cols", "cat_options",
                "num_ranges", "model", "selection", "calibration",
                "operating_point", "metrics", "score_reference", "risk_bands",
                "calibration_curve"):
        assert key in meta, f"metadata is missing '{key}'"


def test_feature_order_matches_the_form(meta):
    assert meta["feature_order"] == INPUT_FEATURES
    assert len(set(meta["feature_order"])) == len(INPUT_FEATURES)


def test_num_and_cat_cols_partition_the_features(meta):
    combined = meta["num_cols"] + meta["cat_cols"]
    assert sorted(combined) == sorted(meta["feature_order"])
    assert not set(meta["num_cols"]) & set(meta["cat_cols"])


# --------------------------------------------------------------------------- #
# data / leakage
# --------------------------------------------------------------------------- #
def test_training_data_has_no_duplicate_observations(data, root, meta):
    """The modelling dataset must not contain repeated observations."""
    modeling = pd.read_csv(root / "data" / "telco_modeling.csv")
    assert modeling.duplicated().sum() == 0
    assert len(modeling) == meta["data"]["rows_modeling"]
    assert meta["data"]["rows_modeling"] + meta["data"]["duplicates_removed"] \
        == meta["data"]["rows_raw"]


def test_no_leaky_columns_in_the_features(meta):
    forbidden = {"Churn_Value", "Churn_Label", "Churn_Score", "CLTV",
                 "Churn_Reason", "CustomerID", "Count", "Country", "State",
                 "City", "Zip_Code", "Lat_Long", "Latitude", "Longitude"}
    assert not forbidden & set(meta["feature_order"])


def test_slider_bounds_match_the_training_data(meta, data):
    """The app must never ask the model to extrapolate."""
    for col, bounds in meta["num_ranges"].items():
        assert bounds["min"] == pytest.approx(float(data[col].min()))
        assert bounds["max"] == pytest.approx(float(data[col].max()))
        assert bounds["min"] <= bounds["median"] <= bounds["max"]


# --------------------------------------------------------------------------- #
# feature construction
# --------------------------------------------------------------------------- #
def test_build_row_has_exactly_the_expected_keys(sample_row):
    row = build_row(**sample_row)
    assert set(row) == set(INPUT_FEATURES)


def test_total_charges_defaults_to_tenure_times_monthly(sample_row):
    row = build_row(**sample_row)
    assert row["Total_Charges"] == pytest.approx(
        sample_row["tenure"] * sample_row["monthly"])


def test_total_charges_can_be_overridden(sample_row):
    sample_row["total_charges"] = 1234.5
    row = build_row(**sample_row)
    assert row["Total_Charges"] == pytest.approx(1234.5)


def test_phone_service_drives_multiple_lines(sample_row):
    sample_row["phone"] = "No"
    row = build_row(**sample_row)
    assert row["Multiple_Lines"] == "No phone service"


def test_no_internet_drives_every_addon(sample_row):
    sample_row["internet"] = "No"
    row = build_row(**sample_row)
    for col in ADDON_COLS:
        assert row[col] == "No internet service"


def test_to_frame_uses_the_training_column_order(sample_row, meta):
    frame = to_frame(build_row(**sample_row), meta)
    assert list(frame.columns) == meta["feature_order"]
    assert len(frame) == 1


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def test_score_is_a_valid_probability(pipe, calibrator, meta, sample_row):
    result = score_customer(pipe, calibrator["estimator"], meta,
                             build_row(**sample_row))
    assert 0.0 <= result["churn_probability"] <= 1.0
    assert 0.0 <= result["raw_score"] <= 1.0
    assert 0.0 <= result["percentile"] <= 100.0


def test_higher_risk_customers_score_higher(pipe, calibrator, meta, sample_row):
    low = dict(sample_row, contract="Two year", tenure=60,
               payment="Credit card (automatic)", monthly=30.0)
    high = dict(sample_row, contract="Month-to-month", tenure=1,
                payment="Electronic check", monthly=110.0)
    low_result = score_customer(pipe, calibrator["estimator"], meta,
                                 build_row(**low))
    high_result = score_customer(pipe, calibrator["estimator"], meta,
                                  build_row(**high))
    assert high_result["churn_probability"] > low_result["churn_probability"]
    assert high_result["percentile"] > low_result["percentile"]


def test_calibration_is_monotone(calibrator, meta):
    raw = np.linspace(0.001, 0.999, 50)
    calibrated = apply_calibrator(calibrator["estimator"],
                                   calibrator["method"], raw)
    assert np.all(np.diff(calibrated) >= -1e-12)


def test_calibration_matches_the_reported_base_rate(meta):
    """The headline number must be a probability, not just a score."""
    cal = meta["calibration"]
    assert cal["mean_calibrated_score_train"] == pytest.approx(
        cal["train_base_rate"], abs=0.02)


def test_percentile_is_monotone_and_bounded(meta):
    quantiles = meta["score_reference"]["quantiles"]
    assert percentile_of(0.0, quantiles) < percentile_of(0.5, quantiles)
    assert percentile_of(0.5, quantiles) < percentile_of(1.0, quantiles)
    assert 0.0 <= percentile_of(-5, quantiles) <= 100.0
    assert 0.0 <= percentile_of(5, quantiles) <= 100.0


def test_risk_bands_are_ordered(meta):
    bands = meta["risk_bands"]
    assert bands["high"]["min_percentile"] > bands["medium"]["min_percentile"]
    assert bands["medium"]["min_percentile"] > bands["low"]["min_percentile"]


def test_band_for_is_threshold_aware(meta):
    """Below the threshold is always 'low'; at/above it is medium or high."""
    thr = meta["operating_point"]["threshold"]
    bands = meta["risk_bands"]
    assert band_for(0.0, bands, thr - 0.01, thr)["name"] == "low"
    assert band_for(0.0, bands, thr + 0.01, thr)["name"] == "medium"
    assert band_for(99.0, bands, thr + 0.01, thr)["name"] == "high"


def test_band_and_threshold_never_disagree(pipe, calibrator, meta, data):
    """The two verdicts shown by the app must always be consistent."""
    thr = meta["operating_point"]["threshold"]
    sample = data.sample(250, random_state=0)
    raw = pipe.predict_proba(sample[meta["feature_order"]])[:, 1]
    probs = apply_calibrator(calibrator["estimator"], calibrator["method"], raw)
    for score, prob in zip(raw, probs):
        band = band_for(
            percentile_of(score, meta["score_reference"]["quantiles"]),
            meta["risk_bands"], float(prob), thr)
        if float(prob) < thr:
            assert band["name"] == "low"
        else:
            assert band["name"] in ("medium", "high")


def test_operating_threshold_gives_the_target_recall(meta):
    op = meta["operating_point"]
    assert op["train_recall"] >= op["target_recall"] - 1e-6


# --------------------------------------------------------------------------- #
# explainability
# --------------------------------------------------------------------------- #
def test_shap_aggregation_adds_up(pipe, calibrator, meta, sample_row):
    import shap
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    row = build_row(**sample_row)
    result = score_customer(pipe, calibrator["estimator"], meta, row)
    explanation = explain(explainer, pipe, meta, result["X_new"])

    assert len(explanation["names"]) == len(INPUT_FEATURES)
    total = explanation["base_value"] + explanation["feature_phi"].sum()
    assert total == pytest.approx(math.log(result["raw_score"] /
                                           (1 - result["raw_score"])),
                                   abs=1e-3)


def test_driver_path_telescopes_to_the_final_probability(pipe, calibrator,
                                                         meta, sample_row):
    import shap
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    row = build_row(**sample_row)
    result = score_customer(pipe, calibrator["estimator"], meta, row)
    explanation = explain(explainer, pipe, meta, result["X_new"])
    path = driver_path(
        explanation["feature_phi"], explanation["base_value"],
        transform=lambda p: apply_calibrator(calibrator["estimator"],
                                             calibrator["method"], p),
    )
    assert path["steps"].sum() == pytest.approx(
        path["final_p"] - path["base_p"], abs=1e-9)
    assert path["final_p"] == pytest.approx(result["churn_probability"],
                                            abs=1e-6)


def test_feature_labels_are_readable(sample_row):
    row = build_row(**sample_row)
    names = INPUT_FEATURES
    labels = feature_labels(names, row)
    assert all(" = " in label for label in labels)
    short, values = feature_name_and_value(names, row)
    assert len(short) == len(values) == len(names)


def test_aggregated_shap_follows_the_feature_it_belongs_to(pipe, meta, sample_row):
    """Switching a category must move the SHAP value of *that* feature."""
    import shap
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    names = INPUT_FEATURES

    def contract_phi(contract):
        row = build_row(**dict(sample_row, contract=contract))
        explanation = explain(explainer, pipe, meta, to_frame(row, meta))
        return float(explanation["feature_phi"][names.index("Contract")])

    month_to_month = contract_phi("Month-to-month")
    two_year = contract_phi("Two year")
    assert month_to_month > two_year, (
        "a month-to-month contract should push the risk up relative to two year")


def test_other_factors_segment_covers_the_remainder(pipe, calibrator, meta,
                                                     sample_row):
    import shap
    explainer = shap.TreeExplainer(pipe.named_steps["model"])
    row = build_row(**sample_row)
    result = score_customer(pipe, calibrator["estimator"], meta, row)
    explanation = explain(explainer, pipe, meta, result["X_new"])
    path = driver_path(
        explanation["feature_phi"], explanation["base_value"],
        transform=lambda p: apply_calibrator(calibrator["estimator"],
                                             calibrator["method"], p),
    )
    covered = sum(len(indices) for indices, _ in path["segments"])
    assert covered == len(INPUT_FEATURES)


# --------------------------------------------------------------------------- #
# reported metrics
# --------------------------------------------------------------------------- #
def test_confusion_matrix_is_consistent(meta):
    cm = meta["metrics"]["confusion_matrix"]
    n_test = meta["model"]["n_test_rows"]
    assert cm["tn"] + cm["fp"] + cm["fn"] + cm["tp"] == n_test


def test_reported_metrics_are_in_range(meta):
    m = meta["metrics"]["test"]
    for key in ("roc_auc", "pr_auc", "precision", "recall", "f1", "accuracy"):
        assert 0.0 <= m[key] <= 1.0, key
    assert m["roc_auc"] > 0.8, "the model should be better than random"
    assert m["recall"] >= 0.7, "recall is what the project optimises for"


def test_model_was_selected_on_the_training_split(meta):
    selection = meta["selection"]
    assert selection["selected"] in selection["candidates"]
    assert "training" in selection["note"].lower()


# --------------------------------------------------------------------------- #
# charts and the app itself
# --------------------------------------------------------------------------- #
def test_charts_render():
    from charts import plot_drivers, plot_reliability, plot_shap_waterfall
    labels = ["Contract = Month-to-month", "Tenure = 3 months"]
    steps = np.array([0.11, -0.04])
    figure = plot_drivers(labels, steps, 0.30, 0.37)
    assert figure is not None
    assert len(figure.data) == 1
    assert list(figure.data[0].y) == labels
    # the bars must start where the previous one ended
    assert list(figure.data[0].base) == [0.30, 0.41]
    assert figure.layout.xaxis.range[0] == 0

    reliability = plot_reliability({
        "predicted": [0.1, 0.5], "actual": [0.08, 0.47], "counts": [10, 10]})
    assert reliability is not None

    shap_figure = plot_shap_waterfall(labels, np.array([0.5, -0.2]), -0.1)
    assert list(shap_figure.data[0].base) == [-0.1, 0.4]


def test_charts_are_responsive():
    """The charts must be SVG, not a fixed size raster.

    A fixed size Matplotlib figure gets scaled down to the column width, which
    shrinks the labels to a few pixels on a narrow screen. Plotly re-lays out
    instead, so the chart has to stay a Plotly figure.
    """
    from charts import plot_drivers
    figure = plot_drivers(["Contract = Month-to-month"], [0.1], 0.3, 0.4)
    assert figure.__class__.__module__.startswith("plotly")
    # automargin keeps the axis labels from being truncated
    assert figure.layout.yaxis.automargin is True
    assert figure.layout.xaxis.automargin is True


def _app_html(app):
    return " ".join(m.value for m in app.markdown)


def _churn_probability(app):
    """The probability the app shows, pulled out of the rendered card."""
    match = re.search(r'card-value"[^>]*>([\d.]+)%', _app_html(app))
    return match.group(1) if match else None


def test_app_runs_without_errors(root):
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(root / "app.py"), default_timeout=180)
    app.run()
    assert not app.exception, f"app raised: {[e.value for e in app.exception]}"
    html = _app_html(app)
    # the styled hero, the KPI strip and the risk card
    assert "hero-title" in html
    assert "kpi-row" in html
    assert "Churn probability" in html
    assert _churn_probability(app) is not None


def test_app_responds_to_a_new_customer(root):
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(root / "app.py"), default_timeout=180)
    app.run()
    before = _churn_probability(app)

    contract = next(w for w in app.sidebar.selectbox if w.label == "Contract")
    contract.set_value("Two year").run()
    assert not app.exception
    after = _churn_probability(app)
    assert after is not None
    assert after != before, "the score should react to the input"


def test_theme_styling_is_applied(root):
    """The page must not fall back to unstyled Streamlit defaults."""
    from streamlit.testing.v1 import AppTest
    from theme import CSS, hero, kpi_row, risk_card

    app = AppTest.from_file(str(root / "app.py"), default_timeout=180)
    app.run()
    assert not app.exception
    assert "hero-title" in _app_html(app)

    # the shared helpers produce the expected markup
    assert "--accent" in CSS and "font-family" in CSS
    assert "hero-title" in hero()
    assert "kpi-value" in kpi_row([("1", "a", "")])
    assert "meter-fill" in risk_card(0.5, "Low risk", "green", 50, 0.3, 0.3)
