"""Design tokens and reusable presentation components.

This module is the single source of truth for the application's visual
language: colour, typography, spacing, radius, and elevation. Components here
return HTML strings and stay free of Streamlit so they can be reused across
pages and tested directly.
"""
from __future__ import annotations

COLOR = {
    "canvas": "#F7F8FA",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F4F8",
    "ink": "#172B4D",
    "ink_soft": "#475467",
    "muted": "#667085",
    "accent": "#356AE6",
    "accent_soft": "#EEF3FF",
    "positive": "#269B78",
    "warning": "#D99A32",
    "danger": "#D9534F",
    "border": "#E6EAF0",
    "border_strong": "#D0D7E2",
    "sidebar": "#0B1220",
    "sidebar_surface": "#111A2B",
    "sidebar_text": "#CBD5E1",
}

SPACE = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "0.75rem",
    "lg": "1rem",
    "xl": "1.5rem",
    "2xl": "2rem",
}

RADIUS = {"sm": "8px", "md": "12px", "lg": "16px", "pill": "999px"}

FONT = {
    "sans": ('Inter, "IBM Plex Sans", -apple-system, BlinkMacSystemFont, '
             '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'),
    "mono": ('"SFMono-Regular", Consolas, "Liberation Mono", Menlo, '
             'monospace'),
}

SHADOW = {
    "card": "0 1px 2px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.05)",
    "panel": "0 1px 2px rgba(15,23,42,0.04)",
}


def variables_css():
    """Return the ``:root`` block that exposes the tokens as CSS variables."""
    return f"""
:root {{
    --canvas: {COLOR['canvas']};
    --surface: {COLOR['surface']};
    --surface-alt: {COLOR['surface_alt']};
    --ink: {COLOR['ink']};
    --ink-soft: {COLOR['ink_soft']};
    --muted: {COLOR['muted']};
    --accent: {COLOR['accent']};
    --accent-soft: {COLOR['accent_soft']};
    --positive: {COLOR['positive']};
    --warning: {COLOR['warning']};
    --danger: {COLOR['danger']};
    --border: {COLOR['border']};
    --border-strong: {COLOR['border_strong']};
    --radius: {RADIUS['md']};
    --radius-sm: {RADIUS['sm']};
    --radius-lg: {RADIUS['lg']};
    --radius-pill: {RADIUS['pill']};
    --shadow-card: {SHADOW['card']};
    --shadow-panel: {SHADOW['panel']};
    --font-sans: {FONT['sans']};
    --font-mono: {FONT['mono']};
}}
"""


def sidebar_brand(product="RETENTION INTELLIGENCE",
                  subtitle="Customer analytics platform"):
    return (
        '<div class="brand">'
        '<div class="brand-mark">R</div>'
        '<div class="brand-copy">'
        f'<div class="brand-name">{product}</div>'
        f'<div class="brand-sub">{subtitle}</div>'
        '<div class="brand-version">v1.0 · Phase 1 foundation</div>'
        '</div></div>'
    )


def section_header(title, caption=""):
    caption_html = (f'<div class="section-caption">{caption}</div>'
                    if caption else "")
    return (
        '<div class="section-head">'
        f'<div class="section-title">{title}</div>'
        f'{caption_html}</div>'
    )


def panel(title, body, caption="", phase=None):
    """A bordered content panel with an optional phase badge."""
    caption_html = (f'<div class="panel-caption">{caption}</div>'
                    if caption else "")
    badge_html = (f'<span class="phase-badge">{phase}</span>'
                  if phase else "")
    return (
        '<div class="panel">'
        '<div class="panel-head"><div>'
        f'<div class="panel-title">{title}</div>'
        f'{caption_html}</div>{badge_html}</div>'
        f'<div class="panel-body">{body}</div>'
        '</div>'
    )


def phase_placeholder(title, phase, description, items=()):
    """A consistent empty-state panel for features planned in later phases."""
    list_items = "".join(f"<li>{item}</li>" for item in items)
    body = (
        f'<p class="placeholder-lead">{description}</p>'
        f'<ul class="planned-list">{list_items}</ul>'
    )
    return panel(title, body, phase=phase)
