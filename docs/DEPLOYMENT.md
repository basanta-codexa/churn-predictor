# Deployment guide

This project is currently deployed as a public Streamlit Community Cloud demo. The notes below describe the supported deployment path and the checks that must be repeated before releasing changes.

## Current deployment

- Entry point: `app.py`
- Pages: registered explicitly with `st.navigation` in the product order
- Runtime: Python 3.14
- Dependencies: `requirements.txt` (pinned)
- Artifacts: `models/model.joblib`, `models/calibrator.joblib`, `models/metadata.json`

Streamlit Community Cloud rebuilds the environment from `requirements.txt` on every push to the connected `main` branch. Allow 1–3 minutes for the rebuild, then hard-refresh the application URL.

## Pre-deployment checklist

1. **Dependencies**
   - Verify `pip install -r requirements.txt` succeeds in a clean environment.
   - Run `python -m pip check`.
2. **Artifacts**
   - Confirm all three files in `models/` exist and are readable.
   - Confirm `metadata.json` has the expected `schema_version`.
   - Do not retrain solely for a UI change.
3. **Prediction workflow**
   - Open **Predict Churn**, change an input, and confirm the score and SHAP explanation update.
   - Confirm the probability is calibrated and the risk band agrees with the threshold.
4. **Analytics**
   - Open **Overview** and confirm KPIs and charts load from the committed data.
   - Open **Customer Intelligence** and test search, filters, pagination, and a small CSV upload.
   - Open **Model Analytics** and confirm the curves, confusion matrix, calibration chart, and model information load.
5. **Tests**
   - Run `pytest tests`. All tests must pass.
6. **Error handling**
   - Confirm a malformed CSV upload reports missing columns rather than crashing.
   - Confirm a missing or inconsistent artifact stops the app with a readable message.
7. **Performance**
   - Confirm the app caches model loading and scored data.
   - Confirm batch prediction is limited to 10,000 rows per file.
8. **Secrets**
   - No credentials are currently required.
   - If authentication is added, store credentials in Streamlit secrets or a secret manager, never in the repository.

## Known limitations

- The demo has no authentication or authorization. Do not expose real customer data through it.
- Customer information is not logged, but the application also has no audit trail.
- Model performance is measured on one held-out split from a static public dataset. It is not production monitoring.
- Drift detection, scheduled retraining, and model rollback are not implemented.

## Local verification

```bash
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
pytest tests
```
