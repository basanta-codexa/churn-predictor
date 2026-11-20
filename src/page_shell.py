"""Shared page setup for the multi-page Streamlit application."""
from __future__ import annotations

import streamlit as st

from theme import CSS, footer, hero, phase_placeholder, sidebar_brand


def setup(page_title, eyebrow, title, subtitle, meta=()):
    """Apply the theme and render the standard brand header and sidebar."""
    st.set_page_config(page_title=page_title, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown(sidebar_brand(), unsafe_allow_html=True)
    st.markdown(
        hero(eyebrow=eyebrow, title=title, subtitle=subtitle, meta=meta),
        unsafe_allow_html=True,
    )


def placeholder(page_title, eyebrow, title, subtitle, phase, description,
                items=(), footer_items=()):
    """Render a consistent placeholder page for a planned phase."""
    setup(page_title, eyebrow, title, subtitle)
    st.markdown(
        phase_placeholder(title, phase, description, items),
        unsafe_allow_html=True,
    )
    if footer_items:
        st.markdown(footer(footer_items), unsafe_allow_html=True)
