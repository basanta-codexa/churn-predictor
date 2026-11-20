"""Presentation layer for the churn application.

A premium light theme: warm grey canvas, white surfaces, deep navy text, and a
single cobalt accent. The sidebar is dark to give the layout weight and clear
separation between navigation and content. All colours, spacing, typography,
and radius values come from :mod:`design`.
"""
from __future__ import annotations

from design import (COLOR, SPACE, RADIUS, FONT, SHADOW, variables_css,
                    sidebar_brand, section_header, panel, phase_placeholder)

CSS = "<style>\n" + variables_css() + f"""
html, body {{
    background: var(--canvas);
    color: var(--ink);
}}

.stApp,
[data-testid="stAppViewContainer"],
section.main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {{
    background: var(--canvas) !important;
}}

.block-container {{
    max-width: 1280px;
    padding-top: {SPACE['xl']};
    padding-bottom: {SPACE['2xl']};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

#MainMenu,
footer,
[data-testid="stDecoration"] {{
    display: none;
}}

.stApp,
.stApp *:not([data-testid="stIconMaterial"]) {{
    font-family: var(--font-sans);
}}

[data-testid="stIconMaterial"] {{
    font-family: "Material Symbols Rounded" !important;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}}

.stApp {{
    font-size: 0.95rem;
}}

.stApp p {{
    line-height: 1.6;
    color: var(--ink-soft);
}}

.stApp h1,
.stApp h2,
.stApp h3 {{
    color: var(--ink);
    letter-spacing: -0.02em;
}}

.stApp h3 {{
    margin-top: {SPACE['xl']};
    margin-bottom: {SPACE['sm']};
}}

.stApp [data-testid="stCaptionContainer"] p {{
    color: var(--muted);
}}

.stApp hr {{
    border-color: var(--border);
}}

/* --------------------------------------------------------------- header */
.hero {{
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    padding: 1.25rem 1.4rem;
    margin-bottom: {SPACE['lg']};
}}

.hero-badge {{
    display: inline-block;
    color: var(--accent);
    background: var(--accent-soft);
    border-radius: var(--radius-sm);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    padding: 0.25rem 0.6rem;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
}}

.hero-title {{
    color: var(--ink);
    font-size: 2.15rem;
    font-weight: 750;
    line-height: 1.1;
    letter-spacing: -0.035em;
    margin: 0;
}}

.hero-sub {{
    color: var(--ink-soft);
    font-size: 0.98rem;
    line-height: 1.6;
    margin-top: 0.55rem;
    max-width: 74ch;
}}

.hero-chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem 1.25rem;
    margin-top: 1rem;
}}

.chip {{
    color: var(--muted);
    font-size: 0.8rem;
    font-weight: 500;
}}

.chip b {{
    color: var(--ink);
    font-weight: 700;
}}

/* ------------------------------------------------------------ kpi strip */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: {SPACE['md']};
    margin: 0 0 {SPACE['xl']};
}}

.kpi {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    border-radius: var(--radius);
    box-shadow: var(--shadow-panel);
    padding: 0.95rem 1.05rem;
}}

.kpi-value {{
    color: var(--ink);
    font-size: 1.65rem;
    font-weight: 750;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.03em;
    line-height: 1.1;
}}

.kpi-label {{
    color: var(--muted);
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}}

.kpi-note {{
    color: var(--muted);
    font-size: 0.76rem;
    margin-top: 0.2rem;
}}

/* ------------------------------------------------------------ risk card */
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow-card);
    height: 100%;
    padding: 1.1rem 1.2rem;
}}

.card-label {{
    color: var(--muted);
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}}

.card-value {{
    color: var(--ink);
    font-size: 2.15rem;
    font-weight: 750;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.035em;
    line-height: 1.05;
}}

.card-note {{
    color: var(--muted);
    font-size: 0.83rem;
    line-height: 1.55;
    margin-top: 0.5rem;
}}

.pill {{
    display: inline-flex;
    align-items: center;
    border: 1px solid transparent;
    border-radius: var(--radius-pill);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin-top: 0.55rem;
    padding: 0.22rem 0.62rem;
}}

.pill-green  {{ background: #E7F6F1; color: #269B78; border-color: #A7DCC8; }}
.pill-orange {{ background: #FDF4E5; color: #D99A32; border-color: #F2D9A6; }}
.pill-red    {{ background: #FCEDEC; color: #D9534F; border-color: #F2C4C2; }}
.pill-slate  {{ background: #F1F4F8; color: #667085; border-color: #E6EAF0; }}

/* ----------------------------------------------------------- risk meter */
.meter-wrap {{
    margin-top: 1rem;
}}

.meter {{
    position: relative;
    height: 8px;
    border-radius: var(--radius-pill);
    background: #E8EDF4;
}}

.meter-fill {{
    height: 100%;
    border-radius: var(--radius-pill);
    background: var(--accent);
}}

.meter-marker {{
    position: absolute;
    top: -4px;
    width: 2px;
    height: 16px;
    border-radius: 1px;
    background: var(--ink);
}}

.meter-legend {{
    display: flex;
    justify-content: space-between;
    gap: 0.4rem;
    color: var(--muted);
    font-size: 0.7rem;
    margin-top: 0.45rem;
}}

.meter-legend span {{
    white-space: nowrap;
}}

.meter-legend .mid {{
    color: var(--ink-soft);
    font-weight: 600;
}}

/* ---------------------------------------------------- sections & panels */
.section-head {{
    margin: {SPACE['xl']} 0 {SPACE['md']};
}}

.section-title {{
    color: var(--ink);
    font-size: 1.05rem;
    font-weight: 700;
}}

.section-caption {{
    color: var(--muted);
    font-size: 0.82rem;
    margin-top: 0.2rem;
}}

.panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow-panel);
    margin-bottom: {SPACE['md']};
    overflow: hidden;
}}

.panel-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: {SPACE['md']};
    padding: 0.9rem 1.1rem;
    border-bottom: 1px solid var(--border);
}}

.panel-title {{
    color: var(--ink);
    font-size: 0.95rem;
    font-weight: 700;
}}

.panel-caption {{
    color: var(--muted);
    font-size: 0.79rem;
    margin-top: 0.15rem;
}}

.panel-body {{
    padding: 1rem 1.1rem;
}}

.phase-badge {{
    background: var(--accent-soft);
    color: var(--accent);
    border-radius: var(--radius-sm);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.22rem 0.55rem;
    text-transform: uppercase;
    white-space: nowrap;
}}

.placeholder-lead {{
    color: var(--ink-soft);
    margin-bottom: 0.6rem;
}}

.planned-list {{
    color: var(--muted);
    font-size: 0.85rem;
    margin: 0;
    padding-left: 1.1rem;
}}

.planned-list li {{
    margin-bottom: 0.3rem;
}}

/* --------------------------------------------------------------- charts */
[data-testid="stPlotlyChart"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow-panel);
    padding: 0.25rem;
}}

/* ------------------------------------------------------------- expander */
[data-testid="stExpander"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}}

[data-testid="stExpander"] summary:hover {{
    background: var(--surface-alt);
}}

/* -------------------------------------------------------------- sidebar */
[data-testid="stSidebar"] {{
    background: {COLOR['sidebar']} !important;
    border-right: 1px solid {COLOR['sidebar_surface']};
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: {SPACE['lg']};
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.35rem 0 0.9rem;
    border-bottom: 1px solid {COLOR['sidebar_surface']};
    margin-bottom: 0.8rem;
}}

.brand-mark {{
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    display: grid;
    place-items: center;
    background: var(--accent);
    color: #FFFFFF;
    border-radius: 9px;
    font-weight: 800;
    font-size: 0.95rem;
}}

.brand-name {{
    color: #F8FAFC;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}}

.brand-sub {{
    color: #94A3B8;
    font-size: 0.72rem;
    margin-top: 0.1rem;
}}

.brand-version {{
    color: #64748B;
    font-size: 0.66rem;
    margin-top: 0.3rem;
}}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #E2E8F0 !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    margin-top: 1.2rem;
    text-transform: uppercase;
}}

[data-testid="stSidebar"] p {{
    color: #94A3B8;
    font-size: 0.78rem;
}}

[data-testid="stSidebar"] label p {{
    color: #CBD5E1;
    font-size: 0.84rem;
}}

/* --------------------------------------------------------------- footer */
.footer {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.25rem;
    align-items: center;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: {SPACE['2xl']};
    padding-top: {SPACE['lg']};
}}

.footer strong {{
    color: var(--ink);
    font-weight: 700;
}}
</style>
"""

#: Background, foreground and solid accent for each risk band.
BAND_COLOURS = {
    "green": ("#E7F6F1", "#269B78", "#269B78"),
    "orange": ("#FDF4E5", "#D99A32", "#D99A32"),
    "red": ("#FCEDEC", "#D9534F", "#D9534F"),
    "slate": ("#F1F4F8", "#667085", "#667085"),
}


def _ordinal(value):
    """Format an integer with an English ordinal suffix."""
    number = int(round(value))
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def hero(eyebrow="", title="Customer Churn Risk", subtitle="", meta=(),
         *, badge=None, chips=None):
    """Render the page header.

    ``badge`` and ``chips`` are accepted as aliases for ``eyebrow`` and
    ``meta`` so callers written against the previous signature keep working.
    """
    if badge is not None:
        eyebrow = badge
    if chips is not None:
        meta = chips
    meta_html = ""
    if meta:
        items = "".join(f'<span class="chip">{item}</span>' for item in meta)
        meta_html = f'<div class="hero-chips">{items}</div>'
    eyebrow_html = f'<div class="hero-badge">{eyebrow}</div>' if eyebrow else ""
    return (
        '<div class="hero">'
        f'{eyebrow_html}'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div>'
        f'{meta_html}'
        '</div>'
    )


def kpi_row(items):
    """``items`` is a list of ``(value, label, note)`` tuples."""
    cells = []
    for value, label, note in items:
        note_html = f'<div class="kpi-note">{note}</div>' if note else ""
        cells.append(
            '<div class="kpi">'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'{note_html}</div>'
        )
    return f'<div class="kpi-row">{"".join(cells)}</div>'


def risk_card(probability, band_label, band_colour, percentile, threshold,
              base_pct):
    """The headline prediction card, with a meter that shows the threshold."""
    background, text, solid = BAND_COLOURS.get(
        band_colour, BAND_COLOURS["slate"])
    meter = (
        '<div class="meter-wrap"><div class="meter">'
        f'<div class="meter-fill" style="width:{min(probability * 100, 100):.1f}%"></div>'
        f'<div class="meter-marker" style="left:{min(threshold * 100, 100):.1f}%"></div>'
        '</div><div class="meter-legend">'
        '<span>0%</span>'
        f'<span class="mid">baseline {base_pct:.0%} &nbsp;·&nbsp; threshold {threshold:.0%}</span>'
        '<span>100%</span>'
        '</div></div>'
    )
    return (
        '<div class="card">'
        '<div class="card-label">Churn probability</div>'
        f'<div class="card-value" style="color:{solid}">{probability:.1%}</div>'
        f'<span class="pill" style="background:{background};color:{text};'
        f'border-color:{text}33">{band_label}</span>'
        f'{meter}'
        f'<div class="card-note">Ranks in the top '
        f'{max(100 - percentile, 1):.0f}% of the training population '
        f'({_ordinal(percentile)} percentile).</div>'
        '</div>'
    )


def percentile_card(percentile, threshold, probability, target_recall=0.80):
    if probability >= threshold:
        state, colour = "Above threshold", "red"
        note = ("Flag this customer for retention outreach. The calibrated "
                "probability is at or above the operating threshold.")
    else:
        state, colour = "Below threshold", "green"
        note = ("No outreach recommended. The calibrated probability is below "
                f"the operating threshold selected for {target_recall:.0%} "
                "recall.")
    background, text, _ = BAND_COLOURS[colour]
    return (
        '<div class="card">'
        '<div class="card-label">Population percentile</div>'
        f'<div class="card-value">{_ordinal(percentile)}</div>'
        f'<span class="pill" style="background:{background};color:{text};'
        f'border-color:{text}33">{state}</span>'
        f'<div class="card-note">{note}</div>'
        '</div>'
    )


def note_card(label, body, note=""):
    note_html = f'<div class="card-note">{note}</div>' if note else ""
    return (
        '<div class="card">'
        f'<div class="card-label">{label}</div>'
        f'<div class="card-note" style="margin-top:.4rem">{body}</div>'
        f'{note_html}</div>'
    )


def footer(items):
    cells = "".join(f"<span><strong>{key}</strong> {value}</span>"
                    for key, value in items)
    return f'<div class="footer">{cells}</div>'
