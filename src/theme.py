"""Presentation layer for the churn app: theme CSS and small HTML components.

The visual language is a dark "aurora" dashboard:

* a soft multi-colour gradient mesh behind the whole page,
* frosted glass cards that float on top of it,
* a gradient display title with a slow shimmer,
* a gradient meter with a light sweep, so the eye lands on the prediction.

Streamlit's own widgets all look the same on every app, so the identity lives
here. The CSS is injected once, at the top of the app.
"""
from __future__ import annotations

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

/* ------------------------------------------------------------- backdrop */
/* Only the page itself is painted. Every container above it has to stay
   transparent, otherwise an opaque child covers the gradient. */
html, body { background-color: #08080F; }
.stApp, [data-testid="stAppViewContainer"], section.main,
[data-testid="stMain"], [data-testid="stMainBlockContainer"],
.block-container {
    background-color: transparent !important;
}
.stApp, [data-testid="stMain"], section.main {
    background-image:
        radial-gradient(1200px 700px at 8% -10%, rgba(124, 58, 237, 0.50), transparent 62%),
        radial-gradient(1000px 560px at 94% -6%, rgba(14, 165, 233, 0.34), transparent 60%),
        radial-gradient(900px 520px at 76% 6%, rgba(168, 85, 247, 0.20), transparent 62%),
        radial-gradient(1200px 680px at 52% 118%, rgba(236, 72, 153, 0.16), transparent 60%);
    background-repeat: no-repeat;
    /* fixed + viewport sized: the page scrolls, the glow stays put */
    background-attachment: fixed;
    background-size: 100% 100vh;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { background: transparent; }
#MainMenu, footer, [data-testid="stDecoration"] { display: none; }

/* ---------------------------------------------------------------- type */
.stApp, .stApp *:not([data-testid="stIconMaterial"]) {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}
/* the icon set uses its own ligature font - overriding it would print the
   raw glyph names ("arrow_left") instead of the icons */
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.stApp { font-size: 0.93rem; }
.stApp p { line-height: 1.55; color: #AEB4C8; }
.stApp h3 {
    color: #F2F3F9; margin-top: 1.5rem; margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
}
.stApp [data-testid="stCaptionContainer"] p { color: #8A90A8; }
.stApp hr { border-color: rgba(255, 255, 255, 0.08); }

/* ---------------------------------------------------------------- hero */
.hero { padding: 0.2rem 0 0.6rem; animation: riseIn 0.6s cubic-bezier(.22,.85,.3,1) both; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(255, 255, 255, 0.055);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #C4B5FD;
    padding: 0.26rem 0.78rem 0.26rem 0.6rem;
    border-radius: 999px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.75rem;
    backdrop-filter: blur(10px);
}
.hero-badge .dot {
    width: 7px; height: 7px; border-radius: 50%; background: #34D399;
    animation: pulse 2.4s ease-in-out infinite;
}
.hero-title {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    font-size: 2.7rem; font-weight: 800; line-height: 1.04; margin: 0;
    background: linear-gradient(95deg, #F5D0FE 0%, #A78BFA 32%, #38BDF8 68%, #F5D0FE 100%);
    background-size: 250% auto;
    -webkit-background-clip: text; background-clip: text; color: transparent;
    animation: shimmer 9s linear infinite;
    filter: drop-shadow(0 8px 34px rgba(139, 92, 246, 0.35));
}
.hero-sub {
    color: #98A0B8; font-size: 1rem; margin-top: 0.5rem; max-width: 62ch;
}
.hero-chips { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.85rem; }
.chip {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #B4BAD0; border-radius: 999px;
    padding: 0.2rem 0.62rem; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.02em; backdrop-filter: blur(8px);
}
.chip b { color: #E6E8F2; font-weight: 700; }

/* ------------------------------------------------------------ kpi strip */
.kpi-row {
    display: flex; gap: 0.6rem; flex-wrap: wrap; margin: 0.15rem 0 0.2rem;
    animation: riseIn 0.6s cubic-bezier(.22,.85,.3,1) 0.08s both;
}
.kpi {
    flex: 1 1 118px; min-width: 112px; position: relative; overflow: hidden;
    background: linear-gradient(170deg, rgba(255,255,255,.075), rgba(255,255,255,.022));
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 15px; padding: 0.7rem 0.8rem;
    backdrop-filter: blur(16px) saturate(150%);
    -webkit-backdrop-filter: blur(16px) saturate(150%);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
    animation: riseIn 0.5s cubic-bezier(.22,.85,.3,1) both;
}
.kpi:nth-child(1) { animation-delay: .10s; }
.kpi:nth-child(2) { animation-delay: .15s; }
.kpi:nth-child(3) { animation-delay: .20s; }
.kpi:nth-child(4) { animation-delay: .25s; }
.kpi:nth-child(5) { animation-delay: .30s; }
.kpi::before {
    content: ''; position: absolute; inset: 0 0 auto 0; height: 2px;
    background: linear-gradient(90deg, #A78BFA, #38BDF8, transparent);
    opacity: .75;
}
.kpi:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 18px 44px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
.kpi-value {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    font-size: 1.35rem; font-weight: 800; line-height: 1.1;
    background: linear-gradient(180deg, #FFFFFF, #BFC6E0);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.kpi-label {
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em;
    color: #8A90A8; font-weight: 700; margin-top: 0.18rem;
}
.kpi-note { font-size: 0.7rem; color: #6E7691; margin-top: 0.1rem; }

/* ------------------------------------------------------------ risk card */
.card {
    position: relative; overflow: hidden;
    background: linear-gradient(170deg, rgba(255,255,255,.075), rgba(255,255,255,.022));
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 17px; padding: 0.95rem 1rem; height: 100%;
    backdrop-filter: blur(16px) saturate(150%);
    -webkit-backdrop-filter: blur(16px) saturate(150%);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    animation: riseIn 0.6s cubic-bezier(.22,.85,.3,1) both;
    transition: transform .25s ease, border-color .25s ease;
}
.card:hover { transform: translateY(-3px); border-color: rgba(255, 255, 255, 0.19); }
.card-label {
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: #8A90A8; font-weight: 700; margin-bottom: 0.3rem;
}
.card-value {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    font-size: 2.1rem; font-weight: 800; line-height: 1.02; letter-spacing: -0.02em;
}
.card-note { font-size: 0.81rem; color: #9AA1B8; margin-top: 0.35rem; line-height: 1.5; }

.pill {
    display: inline-block; padding: 0.2rem 0.66rem; border-radius: 999px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; margin-top: 0.4rem;
    border: 1px solid transparent;
}
.pill-green  { background: rgba(52, 211, 153, 0.14); color: #6EE7B7; border-color: rgba(52, 211, 153, 0.3); }
.pill-orange { background: rgba(251, 191, 36, 0.14); color: #FCD34D; border-color: rgba(251, 191, 36, 0.3); }
.pill-red    { background: rgba(248, 113, 113, 0.15); color: #FCA5A5; border-color: rgba(248, 113, 113, 0.32); }
.pill-slate  { background: rgba(255, 255, 255, 0.07); color: #B4BAD0; border-color: rgba(255, 255, 255, 0.12); }

/* ----------------------------------------------------------- risk meter */
.meter-wrap { margin-top: 0.85rem; }
.meter {
    position: relative; height: 9px; border-radius: 999px;
    background: rgba(255, 255, 255, 0.09); box-shadow: inset 0 1px 2px rgba(0,0,0,.4);
}
.meter-fill {
    height: 100%; border-radius: 999px; position: relative; overflow: hidden;
    background: linear-gradient(90deg, #A78BFA 0%, #7C3AED 45%, #38BDF8 100%);
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.6);
}
.meter-fill::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent);
    transform: translateX(-100%);
    animation: sweep 3.2s ease-in-out infinite;
}
.meter-marker {
    position: absolute; top: -4px; width: 2px; height: 17px;
    background: #94A3B8; border-radius: 1px; box-shadow: 0 0 6px rgba(0,0,0,.6);
}
.meter-legend {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 0.67rem; color: #6E7691; margin-top: 0.4rem; gap: 0.4rem;
}
.meter-legend span { white-space: nowrap; }
.meter-legend .mid { color: #8A90A8; font-weight: 600; }

/* -------------------------------------------------------------- charts */
[data-testid="stPlotlyChart"] {
    background: linear-gradient(170deg, rgba(255,255,255,.05), rgba(255,255,255,.015));
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px; padding: 0.3rem 0.4rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 16px 46px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    animation: riseIn 0.7s cubic-bezier(.22,.85,.3,1) 0.12s both;
}

/* ---------------------------------------------------------- expander */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 14px;
    overflow: hidden;
}
[data-testid="stExpander"] summary:hover { background: rgba(255,255,255,.04); }

/* -------------------------------------------------------------- sidebar */
[data-testid="stSidebar"] {
    background: rgba(6, 6, 13, 0.82) !important;
    backdrop-filter: blur(20px) saturate(140%);
    -webkit-backdrop-filter: blur(20px) saturate(140%);
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #E4E7F2; letter-spacing: 0.09em; text-transform: uppercase;
    font-size: 0.68rem; font-weight: 700; margin-top: 1.1rem;
}
[data-testid="stSidebar"] p { color: #7C8399; font-size: 0.73rem; }
[data-testid="stSidebar"] label p { color: #C3C9DC; font-size: 0.82rem; }

/* --------------------------------------------------------------- footer */
.footer {
    margin-top: 2.4rem; padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    color: #6E7691; font-size: 0.73rem;
    display: flex; gap: 1.3rem; flex-wrap: wrap; align-items: center;
}
.footer strong { color: #A9B0C6; font-weight: 700; }

/* ----------------------------------------------------------- animations */
@keyframes riseIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    to { background-position: 250% center; }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.22); }
    50%      { box-shadow: 0 0 0 7px rgba(52, 211, 153, 0.04); }
}
@keyframes sweep {
    0%   { transform: translateX(-100%); }
    60%  { transform: translateX(100%); }
    100% { transform: translateX(100%); }
}
@media (prefers-reduced-motion: reduce) {
    .hero, .kpi, .kpi-row, .card, [data-testid="stPlotlyChart"],
    .hero-title, .hero-badge .dot, .meter-fill::after { animation: none !important; }
}
</style>
"""

#: Colour and gradient of each risk band.
BAND_COLOURS = {
    "green": ("rgba(52, 211, 153, 0.14)", "#6EE7B7", "linear-gradient(180deg,#FFFFFF,#6EE7B7)"),
    "orange": ("rgba(251, 191, 36, 0.14)", "#FCD34D", "linear-gradient(180deg,#FFFFFF,#FCD34D)"),
    "red": ("rgba(248, 113, 113, 0.15)", "#FCA5A5", "linear-gradient(180deg,#FFFFFF,#FCA5A5)"),
    "slate": ("rgba(255, 255, 255, 0.07)", "#B4BAD0", "linear-gradient(180deg,#FFFFFF,#B4BAD0)"),
}

#: Long category values are trimmed so the axis labels stay readable.
SHORT_VALUES = {
    "Bank transfer (automatic)": "Bank transfer (auto)",
    "Credit card (automatic)": "Credit card (auto)",
    "No internet service": "No internet",
    "No phone service": "No phone",
}


def _short(value):
    text = str(value)
    return SHORT_VALUES.get(text, text)


def _gradient_text(gradient):
    return (f"background:{gradient};-webkit-background-clip:text;"
            f"background-clip:text;color:transparent;")


def hero(badge="Live demo", title="Customer Churn Predictor", subtitle="",
         chips=()):
    chip_html = ""
    if chips:
        items = "".join(f'<span class="chip">{c}</span>' for c in chips)
        chip_html = f'<div class="hero-chips">{items}</div>'
    return (
        '<div class="hero">'
        f'<div class="hero-badge"><span class="dot"></span>{badge}</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div>'
        f'{chip_html}'
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
    background, text, gradient = BAND_COLOURS.get(
        band_colour, BAND_COLOURS["slate"])
    meter = (
        '<div class="meter-wrap"><div class="meter">'
        f'<div class="meter-fill" style="width:{min(probability * 100, 100):.1f}%"></div>'
        f'<div class="meter-marker" style="left:{min(threshold * 100, 100):.1f}%"></div>'
        '</div><div class="meter-legend">'
        '<span>0%</span>'
        f'<span class="mid">avg {base_pct:.0%} &nbsp;·&nbsp; threshold {threshold:.0%}</span>'
        '<span>100%</span>'
        '</div></div>'
    )
    return (
        '<div class="card">'
        '<div class="card-label">Churn probability</div>'
        f'<div class="card-value" style="{_gradient_text(gradient)}">'
        f'{probability:.1%}</div>'
        f'<span class="pill" style="background:{background};color:{text};'
        f'border-color:{text}33">{band_label}</span>'
        f'{meter}'
        f'<div class="card-note">Ranks in the top '
        f'{max(100 - percentile, 1):.0f}% of the customers the model was '
        f'trained on ({percentile:.0f}th percentile).</div>'
        '</div>'
    )


def percentile_card(percentile, threshold, probability):
    if probability >= threshold:
        state, colour = "Above threshold", "red"
        note = ("Flag this customer for retention outreach - the "
                "calibrated probability clears the operating threshold.")
    else:
        state, colour = "Below threshold", "green"
        note = ("No outreach needed: the calibrated probability is under the "
                "operating threshold chosen for 80% recall.")
    background, text, _ = BAND_COLOURS[colour]
    return (
        '<div class="card">'
        '<div class="card-label">Population percentile</div>'
        '<div class="card-value" style="'
        'background:linear-gradient(180deg,#FFFFFF,#C7CDE4);'
        '-webkit-background-clip:text;background-clip:text;color:transparent;">'
        f'{percentile:.0f}th</div>'
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
    cells = "".join(f"<span><strong>{k}</strong> {v}</span>" for k, v in items)
    return f'<div class="footer">{cells}</div>'
