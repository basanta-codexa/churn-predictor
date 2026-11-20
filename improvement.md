# CUSTOMER CHURN PREDICTOR
## Development & UI Transformation Blueprint
### From Machine Learning Project to Enterprise-Grade SaaS Platform

---

# 1. PROJECT OBJECTIVE

Transform the existing Customer Churn Predictor into a polished, professional, enterprise-grade customer analytics and retention intelligence platform.

The application should look and feel like a commercial SaaS product rather than a basic machine-learning demonstration.

The platform should help businesses:

- Understand customer churn patterns.
- Identify customers who are likely to leave.
- Estimate individual customer churn probabilities.
- Understand why customers are at risk.
- Identify important churn-driving factors.
- Explore customer segments.
- Generate batch churn predictions.
- Recommend appropriate retention actions.
- Monitor machine-learning model performance.

The final product should have a professional interface, meaningful analytics, explainable predictions, reliable functionality, and a deployment-ready architecture.

# 2. EXISTING PROJECT: PRESERVE WORKING FUNCTIONALITY

The existing GitHub repository is:

https://github.com/basanta-codexa/churn-predictor

Before making changes, inspect the complete repository and understand its architecture.

Existing functionality to preserve:

- Customer churn dataset and preprocessing.
- Existing feature engineering.
- Trained XGBoost model.
- Saved model artifacts.
- Probability calibration.
- Existing prediction pipeline.
- SHAP explainability.
- Model evaluation.
- Existing Plotly visualizations.
- Model metadata.
- Existing automated tests.

Important rules:

1. Do not retrain the model unless there is a specific technical reason.
2. Do not change the feature order expected by the model.
3. Do not remove existing preprocessing.
4. Do not replace the calibrated prediction pipeline with raw predictions.
5. Do not modify model artifacts unnecessarily.
6. Do not invent model performance metrics.
7. Do not invent customer records, revenue, or business statistics.
8. Maintain backward compatibility wherever practical.
9. Run existing tests after significant modifications.
10. Keep the existing working architecture unless a migration is justified.

First inspect the actual repository files. Never assume that a component exists just because it appears in a proposed architecture.

# 3. PRODUCT IDENTITY AND DESIGN SYSTEM

Product name:

Retention Intelligence

Product category:

Customer Analytics & Churn Prediction Platform

Design direction:

Premium Enterprise SaaS Analytics.

Visual inspiration:

- Stripe Dashboard
- Linear
- Vercel
- Modern enterprise analytics platforms
- Professional customer success software

## Color system

Use a restrained light theme.

Primary background: #F7F8FA

Main surfaces: #FFFFFF

Primary text: #172B4D

Secondary text: #667085

Primary blue: #356AE6

Border: #E6EAF0

High-risk red: #D9534F

Medium-risk amber: #D99A32

Low-risk teal: #269B78

Muted background: #F1F4F8

Use these colors consistently.

## Typography

Preferred fonts:

- Inter
- Geist
- IBM Plex Sans

Use a consistent typography hierarchy.

Page headings should be clear and moderately sized.

Metric values should be visually prominent.

Supporting descriptions should remain readable and understated.

## Design principles

- Strong visual hierarchy.
- Consistent spacing.
- Precise alignment.
- Clean data visualization.
- Minimal decorative elements.
- Subtle borders.
- Restrained shadows.
- Professional tables.
- Consistent iconography.
- Responsive layouts.
- Accessible color contrast.

Avoid:

- Excessive gradients.
- Neon colors.
- Excessive rounded cards.
- Unnecessary animations.
- Oversized headings.
- Decorative charts without analytical value.
- Generic AI-generated dashboard patterns.
- Fake statistics.
- Unnecessary empty space.

The application should feel designed by a professional product design team.

# 4. APPLICATION NAVIGATION AND PAGE STRUCTURE

Create a consistent application navigation system.

The sidebar should contain:

1. Overview
2. Predict Churn
3. Customer Intelligence
4. Retention Insights
5. Model Analytics
6. Settings

Each page should have a consistent header, navigation state, typography, spacing, and component styling.

The sidebar should include:

- Product logo.
- Product name.
- Navigation links.
- Active page indicator.
- Version information.
- Optional account section.

# 5. PAGE ONE: BUSINESS OVERVIEW

This is the primary landing page.

Its purpose is to give users an immediate understanding of customer churn and customer risk.

## Header

Title: Customer Intelligence

Description:

Monitor customer health, identify churn risks, and discover retention opportunities.

Include:

- Dataset information.
- Last updated timestamp, when available.
- Dataset refresh action, if supported.
- Date filter only when the underlying data supports it.

## KPI section

Create professional KPI components.

Potential metrics:

1. Total Customers
2. Churn Rate
3. High-Risk Customers
4. Average Churn Probability

Additional metrics can be introduced only when the required data exists.

For example, Revenue at Risk should only appear if reliable customer revenue information is available.

Each KPI should contain:

- Metric title.
- Metric value.
- Short explanation.
- Optional comparison with a valid previous period.

Never fabricate comparisons or trends.

## Churn distribution

Create a chart showing:

- Low-risk customers.
- Medium-risk customers.
- High-risk customers.

Risk categories must use configurable thresholds.

Make it possible to understand the proportion of customers in each category.

## Churn analytics

Include useful charts:

- Churned versus retained customers.
- Churn distribution by contract type.
- Churn distribution by payment method.
- Churn distribution by tenure.
- Churn probability distribution.

Only display charts supported by actual dataset columns.

## Customer risk overview

Show a compact table containing:

- Customer identifier.
- Churn probability.
- Risk category.
- Selected customer attributes.

Allow users to navigate to the detailed customer assessment.

# 6. PAGE TWO: PREDICT CHURN

This page should provide a polished individual customer prediction experience.

## Customer input form

Create a logically organized form.

Group customer information into sections.

Possible groups:

A. Customer Profile

- Customer tenure.
- Gender, if present in the dataset.
- Senior citizen status, if present.
- Dependents.
- Partner.

B. Subscription Information

- Contract type.
- Internet service.
- Phone service.
- Online security.
- Online backup.
- Device protection.
- Technical support.
- Streaming services.

C. Billing Information

- Payment method.
- Monthly charges.
- Total charges.
- Paperless billing.

Use the exact feature names, categories, data types, and validation rules expected by the existing preprocessing pipeline.

Do not assume every listed feature exists.

## Prediction action

Create a prominent Predict Churn button.

When clicked:

1. Validate the input.
2. Send data through the existing prediction pipeline.
3. Obtain calibrated churn probability.
4. Determine the risk category.
5. Calculate available explanations.
6. Display the results.

## Prediction results

Display:

- Churn probability.
- Risk classification.
- Model prediction.
- Relevant customer attributes.
- Explanation of the prediction.

Use a clean probability visualization.

Example:

Customer Churn Probability: 78%

Risk Classification: High

The example is illustrative only.

Clearly explain that probability is a model estimate, not a guaranteed outcome.

# 7. PAGE THREE: CUSTOMER INTELLIGENCE

Create a customer exploration and analysis page.

Features:

- Customer directory.
- Search functionality.
- Customer filtering.
- Risk category filters.
- Probability sorting.
- Contract-type filtering.
- Customer detail view.
- Customer risk ranking.

The customer table should support:

- Customer ID.
- Churn probability.
- Risk category.
- Tenure.
- Contract type.
- Monthly charges, if available.

Include pagination for larger datasets.

Allow users to select a customer and inspect the prediction.

Do not expose unnecessary sensitive customer information.

## Batch prediction

Allow CSV upload.

Workflow:

1. Upload customer CSV.
2. Validate column names.
3. Validate required features.
4. Check missing values.
5. Apply existing preprocessing.
6. Generate predictions.
7. Display prediction results.
8. Allow CSV download.

Batch predictions must use the same preprocessing, feature ordering, calibration, and prediction logic as individual predictions.

# 8. PAGE FOUR: RETENTION INSIGHTS

This page should turn predictions into understandable business actions.

Include:

## Customer risk segmentation

Analyze:

- High-risk customers.
- Medium-risk customers.
- Low-risk customers.

## Churn drivers

Use existing SHAP explanations and available model information.

Show:

- Important churn-driving features.
- Features associated with increased risk.
- Features associated with reduced risk.
- Customer-level explanation.

Clearly distinguish model associations from proven causes.

## Retention recommendations

Examples:

High-risk customers:

- Review subscription experience.
- Investigate service complaints.
- Evaluate pricing concerns.
- Consider a personalized retention offer.

Medium-risk customers:

- Monitor engagement.
- Review customer satisfaction.
- Identify opportunities for proactive communication.

Low-risk customers:

- Maintain service quality.
- Encourage continued engagement.
- Identify opportunities for loyalty programs.

Recommendations should be linked to available customer information.

Do not claim that a retention action will definitely prevent churn.

# 9. PAGE FIVE: MODEL ANALYTICS

This page should demonstrate the technical quality of the ML system.

Include:

## Performance metrics

- ROC-AUC.
- PR-AUC.
- Precision.
- Recall.
- F1-score.
- Accuracy.
- Brier score.

Only display metrics actually calculated and stored by the existing evaluation pipeline.

## Visualizations

- ROC curve.
- Precision-recall curve.
- Confusion matrix.
- Probability calibration curve.
- Feature importance.
- SHAP summary plot.

## Model information

Display:

- Model type.
- Training information, if recorded.
- Dataset information.
- Model version.
- Calibration status.
- Evaluation date, if available.

Clearly distinguish training performance from held-out test performance.

Avoid claiming production performance based solely on test-set results.

# 10. PAGE SIX: SETTINGS

Create a simple configuration page.

Possible features:

- Risk classification thresholds.
- Dataset management.
- Model information.
- Application configuration.
- Prediction settings.
- Data export.
- Application version.

Do not allow users to modify critical model parameters without validation and appropriate permissions.

# 11. TECHNICAL ARCHITECTURE

Preserve the current Streamlit-based architecture initially.

Recommended structure:

customer-churn-predictor/

    app.py

    pages/

        1_Overview.py

        2_Predict_Churn.py

        3_Customer_Intelligence.py

        4_Retention_Insights.py

        5_Model_Analytics.py

        6_Settings.py

    src/

        predictor.py

        preprocessing.py

        explainability.py

        metrics.py

        data_loader.py

        theme.py

    components/

        sidebar.py

        header.py

        metric_cards.py

        charts.py

        customer_table.py

        prediction_result.py

    styles/

        theme.css

    model/

        model.joblib

        calibrator.joblib

        metadata.json

    tests/

    requirements.txt

This is a proposed organization. Adapt it to the actual repository and preserve existing file paths where changing them provides no benefit.

## Technology stack

Frontend:

- Streamlit
- Python
- Custom CSS

Visualizations:

- Plotly

Machine learning:

- XGBoost
- Scikit-learn
- SHAP
- Joblib

Data:

- Pandas
- NumPy

Optional future backend:

- Flask or FastAPI, if a separate prediction service is genuinely needed.

Do not introduce unnecessary dependencies.

# 12. PRODUCTION READINESS

Before deployment, implement:

## Reliability

- Input validation.
- Error handling.
- Logging.
- Missing-value handling.
- Consistent prediction responses.
- Model-loading validation.
- Safe file uploads.

## Security

- Secure configuration.
- Environment variables.
- No hardcoded credentials.
- File upload restrictions.
- Authentication.
- Authorization.
- Protection of customer information.
- Avoid logging personal customer data.

## Performance

- Cache model loading.
- Avoid recalculating expensive visualizations unnecessarily.
- Optimize large CSV processing.
- Add pagination.
- Prevent repeated unnecessary model loading.

## Testing

Run existing tests.

Add tests for:

- Prediction correctness.
- Preprocessing consistency.
- Probability calibration.
- Input validation.
- Invalid CSV uploads.
- Missing features.
- SHAP output.
- API integration, if applicable.
- UI workflow.

Do not consider the application production-ready simply because it runs locally.

# 13. DEPLOYMENT

Prepare the project for cloud hosting.

Possible deployment options:

- Streamlit Community Cloud for a simple public demo.
- Render for a more controlled application deployment.
- Other suitable cloud hosting depending on resource requirements.

Before deployment:

1. Verify dependency versions.
2. Verify model artifacts.
3. Test clean installation.
4. Test the complete prediction workflow.
5. Test CSV upload and download.
6. Configure secrets securely.
7. Test error handling.
8. Verify application performance.
9. Document deployment steps.

Use authentication and appropriate access controls if real customer information is involved.

# 14. IMPLEMENTATION ORDER

Work in the following sequence.

PHASE 1 — Repository inspection

- Inspect all files.
- Understand existing architecture.
- Identify reusable components.
- Identify missing functionality.
- Establish a working baseline.

PHASE 2 — Design foundation

- Build light theme.
- Establish design tokens.
- Create reusable components.
- Redesign navigation.
- Improve page layout.

PHASE 3 — Business overview

- Build KPI components.
- Add churn distribution.
- Add supported charts.
- Add customer risk overview.

PHASE 4 — Prediction experience

- Redesign customer form.
- Integrate existing prediction logic.
- Display calibrated probability.
- Add SHAP explanations.

PHASE 5 — Customer intelligence

- Customer table.
- Search and filtering.
- Batch CSV prediction.
- Export functionality.

PHASE 6 — Retention insights

- Risk segmentation.
- SHAP-based explanations.
- Retention recommendations.

PHASE 7 — Model analytics

- Evaluation metrics.
- Performance charts.
- Calibration.
- Explainability.

PHASE 8 — Production deployment

- Security.
- Testing.
- Optimization.
- Deployment.
- Documentation.

# 15. STRICT DEVELOPMENT RULES FOR AI CODING AGENTS

When working on this repository:

1. Read the existing source code before modifying anything.
2. Understand the current prediction workflow.
3. Preserve existing functionality.
4. Never invent dataset columns.
5. Never invent performance metrics.
6. Never replace working ML logic just for visual improvements.
7. Never remove existing tests.
8. Make incremental changes.
9. Provide complete code for modified files.
10. Explain which files were changed.
11. Run tests after modifications.
12. Report any failing tests honestly.
13. Avoid unnecessary dependencies.
14. Keep the application modular.
15. Ensure the application runs after every major development phase.

If a required feature depends on data that does not exist, explain the limitation and propose an appropriate implementation rather than displaying fabricated information.

# 16. FINAL PRODUCT EXPECTATION

The final application should be:

- Visually polished.
- Professionally designed.
- Easy to navigate.
- Data-driven.
- Explainable.
- Responsive.
- Reliable.
- Maintainable.
- Deployment-ready.

It should look like a real enterprise customer analytics product, not a generic AI-generated dashboard.

The existing machine-learning pipeline should remain the foundation of the application.

The primary objective is to transform the presentation, user experience, analytics capabilities, and deployment quality while protecting the work already completed.

FINAL DEVELOPMENT PRINCIPLE:

PRESERVE THE ML. UPGRADE THE PRODUCT. BUILD INCREMENTALLY. TEST EVERYTHING.