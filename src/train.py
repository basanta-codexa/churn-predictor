"""Train the churn model and save the pipeline, calibrator and metadata.

Methodology
-----------
1.  Load the cleaned dataset and drop exact duplicate observations, so the
    same feature vector never appears in both the train and the test split.
2.  Hold out 20% of the data as a test split. It is scored **once**, at the
    very end, and is never used to choose anything.
3.  Choose the model with 5-fold stratified cross-validation on the training
    split only.
4.  Fit the winning pipeline on the full training split.
5.  Calibrate it. The tree ensemble is trained with class weighting, so its
    raw output is a ranking score rather than a probability. Out-of-fold
    predictions are used to fit a calibrator (isotonic or sigmoid - the one
    with the better cross-validated log loss wins), which turns the score into
    a real churn probability.
6.  Pick the operating threshold on the training data for a target recall,
    because recall is what a retention team is measured on.
7.  Evaluate on the test split and write model + calibrator + metadata.

Run with:  python src/train.py
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, log_loss,
                             precision_recall_curve, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_val_score, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import apply_calibrator, logit  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "telco_clean.csv"
MODELING_DATA_PATH = ROOT / "data" / "telco_modeling.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"
CALIBRATOR_PATH = MODEL_DIR / "calibrator.joblib"
META_PATH = MODEL_DIR / "metadata.json"

TARGET = "Churn_Value"
NUM_COLS = ["Tenure_Months", "Monthly_Charges", "Total_Charges"]
SEED = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
TARGET_RECALL = 0.80
#: Probabilities are clipped to [EPS, 1-EPS] before taking a log loss, so
#: that a calibrator which outputs exactly 0 or 1 cannot blow up the score.
#: Keep this in sync with the notebook.
EPS = 1e-9
QUANTILE_LEVELS = np.round(np.linspace(0.0, 1.0, 101), 4)

#: Tie-break order used when candidates are within one standard error of the
#: best cross-validated score. The three models are statistically
#: indistinguishable on this dataset, so the winner is decided on the
#: requirements of the app rather than on a noise-level difference:
#:   1. XGBoost      - fast, exact TreeSHAP and the smallest artifact
#:   2. Random Forest - explainable, but a bigger artifact and an
#:                      approximation-heavy SHAP implementation
#:   3. Logistic Regression - very interpretable, but a linear model
PREFERENCE_ORDER = ["XGBoost", "Random Forest", "Logistic Regression"]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def git_commit():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def fit_isotonic(p, y):
    est = IsotonicRegression(out_of_bounds="clip")
    est.fit(np.asarray(p, dtype=float), np.asarray(y))
    return est


def fit_sigmoid(p, y):
    est = LogisticRegression()
    est.fit(logit(p).reshape(-1, 1), np.asarray(y))
    return est


def fit_calibrator(method, p, y):
    return fit_isotonic(p, y) if method == "isotonic" else fit_sigmoid(p, y)


def choose_threshold(probs, y, target_recall):
    """Highest-precision threshold that still reaches ``target_recall``."""
    precision, recall, thresholds = precision_recall_curve(y, probs)
    precision, recall, thresholds = precision[:-1], recall[:-1], thresholds[:-1]
    feasible = np.flatnonzero(recall >= target_recall)
    if feasible.size == 0:                       # target unreachable: take the
        idx = int(np.argmax(recall))            # most sensitive point
    else:
        best_precision = precision[feasible].max()
        candidates = feasible[precision[feasible] >= best_precision - 1e-12]
        idx = int(candidates[np.argmax(recall[candidates])])
    return float(thresholds[idx]), float(precision[idx]), float(recall[idx])


# --------------------------------------------------------------------------- #
# pipeline
# --------------------------------------------------------------------------- #
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Total_Charges"] = pd.to_numeric(df["Total_Charges"], errors="coerce")
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    print(f"[data] {before} rows -> {len(df)} after removing "
          f"{removed} exact duplicate observations")
    df.to_csv(MODELING_DATA_PATH, index=False)
    X = df.drop(columns=[TARGET])
    y = df[TARGET].to_numpy()
    return X, y, removed


def build_preprocessor(cat_cols):
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, NUM_COLS),
        ("cat", categorical_pipe, cat_cols),
    ])


def candidate_models(scale_pos_weight):
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=SEED),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight="balanced",
            random_state=SEED, n_jobs=-1),
        "XGBoost": XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            scale_pos_weight=scale_pos_weight, eval_metric="logloss",
            random_state=SEED),
    }


def select_model(selection):
    """Pick the winner with the one-standard-error rule.

    The candidates are usually within noise of each other. We therefore take
    every model whose cross-validated score is within one standard error of
    the best one and break the tie with the declared preference order, instead
    of chasing a difference that the data cannot support.
    """
    best_name = max(selection, key=lambda n: selection[n]["cv_roc_auc_mean"])
    best_mean = selection[best_name]["cv_roc_auc_mean"]
    best_std = selection[best_name]["cv_roc_auc_std"]
    cutoff = best_mean - best_std
    feasible = [n for n in selection if selection[n]["cv_roc_auc_mean"] >= cutoff]
    chosen = next(n for n in PREFERENCE_ORDER if n in feasible)
    reason = (
        f"best CV ROC-AUC {best_mean:.4f} ({best_name}); candidates within one "
        f"standard error (>= {cutoff:.4f}): {', '.join(sorted(feasible))}. "
        f"Chose {chosen} on the declared preference order (exact/fast TreeSHAP "
        f"explanations and a small artifact)."
        if chosen != best_name else
        f"best CV ROC-AUC {best_mean:.4f} ({best_name}), clearly ahead of the "
        f"one-standard-error cutoff of {cutoff:.4f}."
    )
    return chosen, reason, {
        "best_mean": best_mean,
        "best_std": best_std,
        "one_se_cutoff": round(float(cutoff), 4),
        "candidates_within_one_se": sorted(feasible),
        "preference_order": PREFERENCE_ORDER,
    }


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    print("=" * 68)
    print("Churn model training")
    print("=" * 68)

    X, y, duplicates_removed = load_data()
    cat_cols = [c for c in X.columns if c not in NUM_COLS]

    # --- 1. split off the test set (touched only at the end) --------------- #
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y)
    print(f"[split] train={len(X_train)}  test={len(X_test)}  "
          f"churn rate train={y_train.mean():.3f} test={y_test.mean():.3f}")

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)

    # --- 2. model selection on the training split only --------------------- #
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    candidates = candidate_models(scale_pos_weight)

    print(f"\n[selection] {CV_FOLDS}-fold stratified CV on the training split")
    selection = {}
    for name, model in candidates.items():
        pipe = Pipeline([("prep", build_preprocessor(cat_cols)), ("model", model)])
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc")
        selection[name] = {
            "cv_roc_auc_mean": round(float(scores.mean()), 4),
            "cv_roc_auc_std": round(float(scores.std()), 4),
        }
        print(f"  {name:22s} ROC-AUC {scores.mean():.4f} (+/- {scores.std():.4f})")

    best_name, selection_reason, selection_detail = select_model(selection)
    print(f"[selection] winner: {best_name}")
    print(f"[selection] {selection_reason}")

    # --- 3. fit the winner on the full training split ---------------------- #
    best_pipe = Pipeline([
        ("prep", build_preprocessor(cat_cols)),
        ("model", candidates[best_name]),
    ])
    best_pipe.fit(X_train, y_train)

    # --- 4. calibration on out-of-fold predictions ------------------------- #
    print(f"\n[calibration] generating out-of-fold predictions for {best_name}")
    oof_pipe = Pipeline([
        ("prep", build_preprocessor(cat_cols)),
        ("model", candidate_models(scale_pos_weight)[best_name]),
    ])
    oof = cross_val_predict(oof_pipe, X_train, y_train, cv=cv,
                             method="predict_proba")[:, 1]

    # compare the two calibration methods with an inner CV over the OOF scores
    calib_scores = {}
    for method in ("isotonic", "sigmoid"):
        preds = np.zeros(len(y_train))
        for tr, te in cv.split(oof.reshape(-1, 1), y_train):
            est = fit_calibrator(method, oof[tr], y_train[tr])
            preds[te] = apply_calibrator(est, method, oof[te])
        calib_scores[method] = float(log_loss(y_train, np.clip(preds, EPS, 1 - EPS)))
        print(f"  {method:9s} CV log loss {calib_scores[method]:.4f}")

    calib_method = min(calib_scores, key=calib_scores.get)
    calibrator = fit_calibrator(calib_method, oof, y_train)
    print(f"[calibration] using '{calib_method}' calibration "
          f"(best CV log loss {calib_scores[calib_method]:.4f})")

    oof_calibrated = apply_calibrator(calibrator, calib_method, oof)

    # --- 5. operating point ------------------------------------------------ #
    threshold, oof_precision, oof_recall = choose_threshold(
        oof_calibrated, y_train, TARGET_RECALL)
    print(f"[operating point] threshold={threshold:.3f} chosen on training data "
          f"for recall >= {TARGET_RECALL:.0%} "
          f"(train precision {oof_precision:.3f}, recall {oof_recall:.3f})")

    # --- 6. evaluate ONCE on the test split -------------------------------- #
    test_raw = best_pipe.predict_proba(X_test)[:, 1]
    test_prob = apply_calibrator(calibrator, calib_method, test_raw)
    test_pred = test_prob >= threshold

    tn, fp, fn, tp = confusion_matrix(y_test, test_pred).ravel()
    test_metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, test_raw)), 4),
        "pr_auc": round(float(average_precision_score(y_test, test_prob)), 4),
        "precision": round(float(precision_score(y_test, test_pred)), 4),
        "recall": round(float(recall_score(y_test, test_pred)), 4),
        "f1": round(float(f1_score(y_test, test_pred)), 4),
        "accuracy": round(float((test_pred == y_test).mean()), 4),
        "brier": round(float(brier_score_loss(y_test, test_prob)), 4),
        "log_loss": round(float(log_loss(y_test, np.clip(test_prob, EPS, 1 - EPS))), 4),
    }
    print(f"\n[test] {test_metrics}")
    print(f"[test] confusion matrix  TN={tn} FP={fp} FN={fn} TP={tp}")

    # calibration curve of the final model on the test split
    frac_pos, mean_pred = calibration_curve(y_test, test_prob, n_bins=10,
                                            strategy="quantile")
    counts = np.histogram(test_prob, bins=np.linspace(0, 1, 11))[0]
    calibration_curve_data = {
        "predicted": [round(float(v), 4) for v in mean_pred],
        "actual": [round(float(v), 4) for v in frac_pos],
        "counts": [int(c) for c in counts],
    }
    print(f"[test] mean predicted {test_prob.mean():.3f} vs actual base rate "
          f"{y_test.mean():.3f} (calibration gap "
          f"{test_prob.mean() - y_test.mean():+.3f})")

    # --- 7. reference distribution for percentiles ------------------------- #
    train_scores = best_pipe.predict_proba(X_train)[:, 1]
    score_quantiles = [round(float(q), 6) for q in
                       np.quantile(train_scores, QUANTILE_LEVELS)]
    train_calibrated = apply_calibrator(calibrator, calib_method, train_scores)
    high_cut = float(np.quantile(train_scores, 0.80))
    medium_cut = float(np.quantile(train_scores, 0.60))

    # --- 8. write the artifacts -------------------------------------------- #
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(best_pipe, MODEL_PATH)
    joblib.dump({"method": calib_method, "estimator": calibrator}, CALIBRATOR_PATH)

    metadata = {
        "schema_version": 2,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(),
        "library_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit-learn": sklearn.__version__,
            "xgboost": __import__("xgboost").__version__,
        },
        "feature_order": X.columns.tolist(),
        "data": {
            "source": DATA_PATH.name,
            "modeling": MODELING_DATA_PATH.name,
            "rows_raw": int(len(X) + duplicates_removed),
            "rows_modeling": int(len(X)),
            "duplicates_removed": int(duplicates_removed),
        },
        "num_cols": NUM_COLS,
        "cat_cols": cat_cols,
        "cat_options": {
            c: sorted(X[c].dropna().unique().tolist()) for c in cat_cols
        },
        "num_ranges": {
            c: {
                "min": float(X[c].min()),
                "max": float(X[c].max()),
                "median": float(X[c].median()),
            }
            for c in NUM_COLS
        },
        "model": {
            "name": best_name,
            "params": {
                k: v for k, v in best_pipe.named_steps["model"].get_params().items()
                if k in {"n_estimators", "max_depth", "learning_rate",
                         "scale_pos_weight", "class_weight", "eval_metric",
                         "random_state"}
            },
            "encoded_feature_count": int(
                len(best_pipe.named_steps["prep"].get_feature_names_out())),
            "n_training_rows": int(len(X_train)),
            "n_test_rows": int(len(X_test)),
            "duplicates_removed": int(duplicates_removed),
        },
        "selection": {
            "metric": "roc_auc",
            "cv_folds": CV_FOLDS,
            "candidates": selection,
            "selected": best_name,
            "reason": selection_reason,
            **selection_detail,
            "note": ("Selected on cross-validated ROC-AUC over the training "
                     "split only; the test split was scored once at the end."),
        },
        "calibration": {
            "method": calib_method,
            "cv_log_loss": {k: round(v, 4) for k, v in calib_scores.items()},
            "train_base_rate": round(float(y_train.mean()), 4),
            "mean_raw_score_train": round(float(train_scores.mean()), 4),
            "mean_calibrated_score_train": round(float(train_calibrated.mean()), 4),
            "note": ("The raw model output is a ranking score (the model is "
                     "class weighted); the calibrator maps it onto a real "
                     "churn probability."),
        },
        "operating_point": {
            "target_recall": TARGET_RECALL,
            "threshold": round(threshold, 6),
            "train_precision": round(oof_precision, 4),
            "train_recall": round(oof_recall, 4),
            "selected_on": "out-of-fold training predictions",
        },
        "metrics": {
            "test": test_metrics,
            "confusion_matrix": {"tn": int(tn), "fp": int(fp),
                                 "fn": int(fn), "tp": int(tp)},
            "cv": {
                "roc_auc_mean": selection[best_name]["cv_roc_auc_mean"],
                "roc_auc_std": selection[best_name]["cv_roc_auc_std"],
            },
        },
        "calibration_curve": calibration_curve_data,
        "score_reference": {
            "population": "training set",
            "n": int(len(X_train)),
            "quantiles": score_quantiles,
        },
        "risk_bands": {
            "high": {"label": "High risk", "color": "red",
                     "min_percentile": 80.0, "score_cut": round(high_cut, 6),
                     "description": "top 20% of the training population"},
            "medium": {"label": "Medium risk", "color": "orange",
                       "min_percentile": 60.0, "score_cut": round(medium_cut, 6),
                       "description": "next 20% of the training population"},
            "low": {"label": "Low risk", "color": "green",
                    "min_percentile": 0.0, "score_cut": None,
                    "description": "bottom 60% of the training population"},
        },
    }
    META_PATH.write_text(json.dumps(metadata, indent=2))

    print(f"\nSaved model      -> {MODEL_PATH}")
    print(f"Saved calibrator -> {CALIBRATOR_PATH}")
    print(f"Saved metadata   -> {META_PATH}")


if __name__ == "__main__":
    main()
