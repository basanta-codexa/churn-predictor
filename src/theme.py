"""Presentation layer for the churn application.

The interface uses a restrained dark SaaS style: a near-black canvas, solid
bordered surfaces, one accent colour, and clear typographic hierarchy. There
are no gradients, glass effects, or decorative animation. The CSS is injected
once at the top of the app.
"""
from __future__ import annotations

CSS = """
<style>
:root {
    --bg: #0B0D12;
    --surface: #14171F;
    --surface-muted: #1A1E28;
    --border: #242936;
    --border-strong: #333A4A;
    --text: #E6E8EE;
    --text-secondary: #C3C8D4;
    --muted: #8B90A0;
    --accent: #7C8CFF;
    --accent-soft: rgba(124, 140, 255, 0.12);
    --green: #4ADE80;
    --green-soft: rgba(34, 197, 94, 0.12);
    --amber: #FBBF24;
    --amber-soft: rgba(245, 158, 11, 0.12);
    --red: #F87171;
    --red-soft: rgba(239, 68, 68, 0.12);
    --slate: #94A3B8;
    --slate-soft: rgba(148, 163, 184, 0.12);
    --radius: 12px;
    --shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
}

html, body {
    background: var(--bg);
    color: var(--text);
}

.stApp,
[data-testid="stAppViewContainer"],
section.main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    background: var(--bg) !important;
}

.block-container {
    max-width: 1240px;
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu,
footer,
[data-testid="stDecoration"] {
    display: none;
}

.stApp,
.stApp *:not([data-testid="stIconMaterial"]) {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
}

[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}

.stApp {
    font-size: 0.94rem;
}

.stApp p {
    line-height: 1.55;
    color: var(--text-secondary);
}

.stApp h1,
.stApp h2,
.stApp h3 {
    color: var(--text);
    letter-spacing: -0.015em;
}

.stApp h3 {
    margin-top: 1.6rem;
    margin-bottom: 0.6rem;
}

.stApp [data-testid="stCaptionContainer"] p {
    color: var(--muted);
}

.stApp hr {
    border-color: var(--border);
}

/* --------------------------------------------------------------- header */
.hero {
    padding: 0.25rem 0 1.15rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.15rem;
}

.hero-badge {
    display: inline-block;
    color: var(--accent);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.hero-title {
    color: var(--text);
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.025em;
    margin: 0;
}

.hero-sub {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.55;
    margin-top: 0.55rem;
    max-width: 72ch;
}

.hero-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 1.15rem;
    margin-top: 0.9rem;
}

.chip {
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 500;
}

.chip b {
    color: var(--text);
    font-weight: 650;
}

/* ------------------------------------------------------------ kpi strip */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
    margin: 0.9rem 0 1.2rem;
}

.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 0.85rem 1rem;
}

.kpi-value {
    color: var(--text);
    font-size: 1.5rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.kpi-label {
    color: var(--muted);
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0.22rem;
}

.kpi-note {
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: 0.18rem;
}

/* ------------------------------------------------------------ risk card */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    height: 100%;
    padding: 1rem 1.1rem;
}

.card-label {
    color: var(--muted);
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.card-value {
    color: var(--text);
    font-size: 2rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.025em;
    line-height: 1.1;
}

.card-note {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.5;
    margin-top: 0.45rem;
}

.pill {
    display: inline-flex;
    align-items: center;
    border: 1px solid transparent;
    border-radius: 999px;
    font-size: 0.71rem;
    font-weight: 650;
    letter-spacing: 0.02em;
    margin-top: 0.5rem;
    padding: 0.2rem 0.58rem;
}

.pill-green  { background: var(--green-soft); color: var(--green); border-color: #4ADE8033; }
.pill-orange { background: var(--amber-soft); color: var(--amber); border-color: #FBBF2433; }
.pill-red    { background: var(--red-soft); color: var(--red); border-color: #F8717133; }
.pill-slate  { background: var(--slate-soft); color: var(--slate); border-color: #94A3B833; }

/* ----------------------------------------------------------- risk meter */
.meter-wrap {
    margin-top: 0.9rem;
}

.meter {
    position: relative;
    height: 8px;
    border-radius: 999px;
    background: #232936;
}

.meter-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--accent);
}

.meter-marker {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 16px;
    border-radius: 1px;
    background: var(--text);
}

.meter-legend {
    display: flex;
    justify-content: space-between;
    gap: 0.4rem;
    color: var(--muted);
    font-size: 0.69rem;
    margin-top: 0.42rem;
}

.meter-legend span {
    white-space: nowrap;
}

.meter-legend .mid {
    color: var(--text-secondary);
    font-weight: 600;
}

/* --------------------------------------------------------------- charts */
[data-testid="stPlotlyChart"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 0.25rem;
}

/* ------------------------------------------------------------- expander */
[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}

[data-testid="stExpander"] summary:hover {
    background: var(--surface-muted);
}

/* -------------------------------------------------------------- sidebar */
[data-testid="stSidebar"] {
    background: #0E1016 !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 1.15rem;
}

[data-testid="stSidebar"] p {
    color: var(--muted);
    font-size: 0.78rem;
}

[data-testid="stSidebar"] label p {
    color: var(--text-secondary);
    font-size: 0.84rem;
}

/* --------------------------------------------------------------- footer */
.footer {
    display: flex;
    flex-wrap: wrap;
    gap: 1.25rem;
    align-items: center;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: 2rem;
    padding-top: 1rem;
}

.footer strong {
    color: var(--text);
    font-weight: 650;
}
</style>
"""

#: Background, foreground and solid accent for each risk band.
BAND_COLOURS = {
    "green": ("#4ADE8020", "#4ADE80", "#4ADE80"),
    "orange": ("#FBBF2420", "#FBBF24", "#FBBF24"),
    "red": ("#F8717120", "#F87171", "#F87171"),
    "slate": ("#94A3B820", "#94A3B8", "#94A3B8"),
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
