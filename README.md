# Customer Churn Prediction

[![CI](https://github.com/basanta-codexa/churn-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/basanta-codexa/churn-predictor/actions/workflows/ci.yml)

A reproducible machine learning pipeline and Streamlit application for estimating customer churn risk and explaining the factors behind each prediction.

**Live demo:** https://sl-churn-predictor.streamlit.app/

## Scope

This is a demonstration project intended to show an end-to-end modelling, calibration, and explanation workflow. It is not a production decision system. The reported metrics come from a single public dataset and have not been validated on external or temporal data.

## Overview

The project includes:

- a scikit-learn preprocessing and training pipeline;
- model selection with stratified cross-validation on a training split;
- probability calibration fitted on out-of-fold predictions;
- a recall-oriented operating threshold;
- SHAP explanations aggregated back to the original features;
- a Streamlit interface for scoring individual customers.

The test split is held out until the final evaluation and is not used for model selection, calibration, or threshold selection.

## Dataset

Source: IBM Telco Customer Churn sample.

- 7,043 customers and a 26.5% churn rate.
- 19 features after removing identifiers, location fields, and post-churn columns.
- 22 exact duplicate observations are removed before splitting.

The raw file contains `Churn Label`, `Churn Value`, `Churn Score`, `CLTV`, and `Churn Reason`. These columns are excluded because they are either observed after churn or derived from the churn outcome. Customer identifiers and location fields are also excluded from the model.

## Method

### 1. Data preparation

The cleaned dataset is deduplicated, then split into 80% training and 20% test data with stratification on the target. Numeric features are imputed with a constant (zero) and standardised. Categorical features are one-hot encoded with unknown categories ignored. All preprocessing is fitted inside the training folds, not on the full dataset.

### 2. Model selection

Three candidate models are compared with five-fold stratified cross-validation on the training split only:

- logistic regression with balanced class weights;
- random forest with balanced class weights;
- XGBoost with `scale_pos_weight` set from the training class ratio.

The candidates are close on cross-validated ROC-AUC, so the one-standard-error rule is used: models within one standard error of the best score are treated as statistically indistinguishable. One standard error is the fold standard deviation divided by √5. XGBoost is selected by a declared preference order because it provides fast, exact TreeSHAP values and a small model artifact.

### 3. Probability calibration

Class weighting makes the raw model output a ranking score rather than a calibrated probability. A sigmoid (Platt) calibrator and an isotonic calibrator are fitted on out-of-fold predictions. The method with the better cross-validated log loss is selected, then refitted on all out-of-fold predictions.

### 4. Operating point

The decision threshold is selected on out-of-fold calibrated training predictions as the highest-precision threshold that still reaches the target recall of 80%. The threshold is then applied unchanged to the test split.

### 5. Explainability

SHAP values are computed with `TreeExplainer` on the XGBoost model. One-hot encoded columns are summed back into their original feature, producing one attribution per raw feature. The application also converts the additive log-odds path into a probability path so the explanation uses the same scale as the headline prediction.

## Results

### Model comparison

Five-fold cross-validation on the training split:

| Model | CV ROC-AUC |
|---|---:|
| Logistic Regression | 0.8591 ± 0.0154 |
| Random Forest | 0.8629 ± 0.0153 |
| XGBoost | 0.8572 ± 0.0168 |

All three models fall within one standard error of the best score. XGBoost is selected for the explanation and deployment requirements described above.

### Held-out test performance

The test split contains 1,405 rows and a 26.5% churn rate. It is scored once after all model, calibration, and threshold decisions are complete.

| Metric | Value |
|---|---:|
| ROC-AUC | 0.848 |
| PR-AUC | 0.656 |
| Precision | 0.511 |
| Recall | 0.774 |
| F1 | 0.615 |
| Accuracy | 0.744 |
| Brier score | 0.136 |
| Log loss | 0.408 |

At the 29.4% operating threshold:

- 288 churners are identified;
- 84 churners are missed;
- 276 non-churners are flagged for outreach.

The model is optimised for recall because missing a churner is usually more expensive than contacting a customer who would have stayed. The trade-off is a precision of approximately 51%.

### Calibration

The raw model output overstates churn risk because of class weighting. The sigmoid calibrator closes most of the gap:

| | Mean predicted | Actual base rate | Gap |
|---|---:|---:|---:|
| Raw model output | 0.383 | 0.264 | +0.119 |
| Calibrated | 0.268 | 0.264 | +0.003 |

The sigmoid calibrator was selected over isotonic by cross-validated log loss (0.401 vs 0.421).

## Exploratory findings

- Month-to-month customers churn at 42.7%, compared with 2.8% for two-year contracts.
- Fibre optic customers churn at 41.9%, compared with 19.0% for DSL.
- Electronic check users churn at 45.3%, compared with 15–17% for automatic payment methods.
- SHAP attributes the largest effects to contract type, tenure, monthly charges, and the absence of technical support or online security.

These are descriptive associations in the sample. They should be validated with controlled experiments before being treated as causal retention levers.

## Application

The Streamlit application uses a premium light theme with a dark navigation sidebar. Pages are registered explicitly in `app.py` and follow the intended product structure:

- **Overview** — business health and model snapshot;
- **Predict Churn** — the working individual assessment page;
- **Customers**, **Retention Insights**, **Model Analytics**, **Settings** — placeholders that document the planned scope for later phases.

The Predict Churn page provides:

- a customer input panel with options and bounds taken from the training data;
- a calibrated churn probability and a population percentile;
- a threshold-aware risk band;
- a probability-scale driver chart;
- an exact log-odds SHAP attribution;
- a calibration curve and model performance summary;
- a limitations section for intended use.

The Phase 1 redesign establishes the visual foundation only. Prediction logic is unchanged. To regenerate the screenshot after starting the app, run `python scripts/screenshot.py`. The screenshot helper requires Playwright, which is not part of the runtime requirements.

## Reproducing the results

```bash
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To retrain the model and regenerate the artifacts:

```bash
python src/train.py
```

This writes `models/model.joblib`, `models/calibrator.joblib`, `models/metadata.json`, and `data/telco_modeling.csv`.

To run the test suite:

```bash
pytest tests
```

The tests cover the committed artifacts, calibration behaviour, SHAP aggregation, chart rendering, the theme helpers, and the Streamlit app itself.

## Project structure

```text
.
├── app.py                     # Streamlit router and page registration
├── .streamlit/config.toml     # Theme configuration
├── pages/                     # Named application pages
│   ├── 1_Overview.py
│   ├── 2_Predict_Churn.py     # Working assessment page
│   └── 3-6_*.py               # Placeholders for later phases
├── src/
│   ├── design.py              # Colour, typography, spacing, and reusable components
│   ├── page_shell.py          # Shared page setup
│   ├── theme.py               # CSS and HTML components
│   ├── train.py               # Training, selection, calibration, evaluation
│   ├── predictor.py           # Scoring and SHAP logic (no Streamlit dependency)
│   └── charts.py              # Plotly figures
├── tests/                     # pytest suite
├── notebooks/                  # Exploratory analysis and modelling narrative
├── scripts/                    # Notebook builder and screenshot helper
├── models/                     # Model, calibrator, and metadata artifacts
├── data/                       # Raw, cleaned, and modelling datasets
├── images/                     # Figures used in the documentation
├── pytest.ini
└── requirements.txt
```

## Limitations

- The dataset is a static sample with no time dimension. The model cannot capture changing customer behaviour or seasonal effects.
- The model has not been validated on an external dataset. The reported test metrics are an optimistic estimate of real-world performance.
- `Total Charges` is estimated as tenure multiplied by monthly charges unless the actual value is entered in the application. The estimate can shift the score for a small number of customers.
- SHAP values describe associations learned by the model, not causal effects. Retention actions should be tested experimentally.
- Subgroup performance by gender, age, and other protected attributes has not been audited.
- The application is a demonstration, not a production decision system. It has no authentication, audit logging, drift monitoring, or model rollback.

## Tech stack

Python 3.14, pandas, NumPy, scikit-learn, XGBoost, SHAP, Streamlit, Plotly, pytest.

## Data and license

The IBM Telco Customer Churn dataset is a public sample. Refer to its original distribution terms for licensing and attribution.

No license has been specified for the application code in this repository.
