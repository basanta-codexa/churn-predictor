"""Retention Intelligence application entry point.

Pages are registered explicitly so the navigation order reflects the product
structure rather than the filesystem. Prediction logic lives in
``pages/2_Predict_Churn.py`` and is unchanged by the Phase 1 UI work.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

PAGES = [
    st.Page("pages/1_Overview.py", title="Overview"),
    st.Page("pages/2_Predict_Churn.py", title="Predict Churn"),
    st.Page("pages/3_Customer_Intelligence.py", title="Customer Intelligence"),
    st.Page("pages/4_Retention_Insights.py", title="Retention Insights"),
    st.Page("pages/5_Model_Analytics.py", title="Model Analytics"),
    st.Page("pages/6_Settings.py", title="Settings"),
]

st.navigation(PAGES).run()
