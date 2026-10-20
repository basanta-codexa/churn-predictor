"""Figures for the churn app.

The charts are built with Plotly rather than Matplotlib on purpose. Streamlit
lays a Matplotlib figure out at a fixed physical size and then scales the
raster to fit the column, so on a narrow screen the text ends up at four or
five pixels and is unreadable. Plotly renders SVG that re-lays itself out, so
the labels keep a constant size whatever the browser width is, and the
hover tooltips show the exact numbers.
"""
from __future__ import annotations

import plotly.graph_objects as go

RED = "#FB7185"
BLUE = "#60A5FA"
GREY = "#8A90A8"
TEXT = "#C3C9DC"
MUTED = "#6E7691"
GRID = "rgba(255,255,255,0.07)"

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


def driver_labels(names, values):
    """``['Contract = Month-to-month', ...]`` with shortened long values."""
    return [f"{name} = {_short(value)}" for name, value in zip(names, values)]


def plot_drivers(labels, steps, base_p, final_p, name=None, value=None):
    """Waterfall of the risk drivers, in probability points.

    ``labels`` and ``steps`` are parallel lists ordered by impact. The bars
    telescope: they start at the population average and end at the final
    probability, so their sizes always add up to the total change.
    """
    steps = [float(s) for s in steps]
    bases, running = [], float(base_p)
    for step in steps:
        bases.append(running)
        running += step

    colours = [RED if s >= 0 else BLUE for s in steps]
    after = [b + s for b, s in zip(bases, steps)]

    hover = []
    for i, (label, step) in enumerate(zip(labels, steps)):
        detail = f"<br>Factor: {label}"
        if name is not None and value is not None and i < len(name):
            detail = f"<br>Factor: {name[i]} = {value[i]}"
        hover.append(
            f"{step * 100:+.1f} percentage points"
            f"{detail}<br>"
            f"Risk {bases[i]:.1%} &rarr; {after[i]:.1%}"
        )

    # The axis starts at zero (it is a probability) but is only extended as
    # far as the bars actually reach, so the chart is not mostly empty.
    highest = max(bases + after)
    lowest = min(min(bases), min(after))
    x_max = min(1.0, max(0.45, highest + 0.10))
    x_min = 0.0
    height = 120 + 36 * max(len(labels), 1)

    fig = go.Figure(
        go.Bar(
            x=steps,
            y=labels,
            base=bases,
            orientation="h",
            marker=dict(color=colours, line=dict(width=0)),
            text=[f"{s * 100:+.1f} pp" for s in steps],
            textposition="outside",
            textfont=dict(size=12, color=colours),
            cliponaxis=False,
            hovertemplate="%{hovertext}<extra></extra>",
            hovertext=hover,
        )
    )

    fig.update_layout(
        title=dict(
            text=("What moves this customer's churn risk"
                  f"<br><sup>this customer {final_p:.0%} · "
                  f"population average {base_p:.0%}</sup>"),
            font=dict(size=15, color="#EDEFF7"),
            x=0,
            xanchor="left",
            y=0.98,
            yanchor="top",
        ),
        xaxis=dict(
            title=dict(text="Churn probability", font=dict(size=12, color=TEXT)),
            range=[x_min, x_max],
            tickformat=".0%",
            tickfont=dict(size=12, color=TEXT),
            gridcolor=GRID,
            zeroline=False,
            automargin=True,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12, color=TEXT),
            showgrid=False,
            # reserve room for the labels instead of truncating them
            automargin=True,
        ),
        showlegend=False,
        bargap=0.35,
        height=height,
        margin=dict(l=8, r=72, t=76, b=52),
        font=dict(family="Inter, sans-serif", color=TEXT),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#14141F", bordercolor="rgba(255,255,255,0.14)",
                        font=dict(size=12, color="#E8EAF2")),
    )

    # population baseline and where this customer ends up
    fig.add_vline(x=base_p, line=dict(color=GREY, width=1, dash="dash"),
                  layer="below")
    fig.add_vline(x=final_p, line=dict(color="#555", width=1.5), layer="below")
    return fig


def plot_shap_waterfall(labels, phi, base_value):
    """The exact additive SHAP attribution, in log-odds.

    Every bar is the effect of one feature on the model's raw output. The
    bars add up exactly: base value + all the bars = f(x).
    """
    phi = [float(p) for p in phi]
    bases, running = [], float(base_value)
    for value in phi:
        bases.append(running)
        running += value

    colours = [RED if v >= 0 else BLUE for v in phi]
    span = max(abs(min(phi + [base_value])), abs(max(phi + [base_value]))) or 1.0
    x_min = min(bases + [running]) - span * 0.35
    x_max = max(bases + [running]) + span * 0.35

    hover = [
        f"{v:+.3f} log-odds<br>Factor: {label}<br>"
        f"model score {bases[i]:.3f} &rarr; {bases[i] + v:.3f}"
        for i, (label, v) in enumerate(zip(labels, phi))
    ]

    fig = go.Figure(go.Bar(
        x=phi,
        y=labels,
        base=bases,
        orientation="h",
        marker=dict(color=colours, line=dict(width=0)),
        text=[f"{v:+.2f}" for v in phi],
        textposition="outside",
        textfont=dict(size=12, color=colours),
        cliponaxis=False,
        hovertemplate="%{hovertext}<extra></extra>",
        hovertext=hover,
    ))
    fig.update_layout(
        title=dict(text="SHAP values (log-odds), summed to the model score",
                   font=dict(size=14, color="#EDEFF7"), x=0, xanchor="left"),
        xaxis=dict(title=dict(text="Impact on the model score (log-odds)",
                              font=dict(size=12, color=TEXT)),
                   range=[x_min, x_max],
                   tickfont=dict(size=12, color=TEXT),
                   gridcolor=GRID,
                   zeroline=False,
                   automargin=True),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12, color=TEXT),
                   showgrid=False, automargin=True),
        showlegend=False,
        bargap=0.35,
        height=120 + 34 * max(len(labels), 1),
        margin=dict(l=8, r=72, t=56, b=52),
        font=dict(family="Inter, sans-serif", color=TEXT),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#14141F", bordercolor="rgba(255,255,255,0.14)",
                        font=dict(size=12, color="#E8EAF2")),
    )
    fig.add_vline(
        x=base_value, line=dict(color=GREY, width=1, dash="dash"),
        annotation_text=f"E[f(X)] = {base_value:.3f}",
        annotation_position="top left",
        annotation_font=dict(size=11, color=GREY),
    )
    return fig


def plot_reliability(curve):
    """Reliability diagram: predicted probability against observed churn rate."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="perfect calibration",
        line=dict(color=GREY, width=1, dash="dash"),
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=curve["predicted"], y=curve["actual"], mode="lines+markers",
        name="this model",
        line=dict(color=RED, width=2),
        marker=dict(size=9),
        hovertemplate=("predicted %{x:.1%}<br>observed %{y:.1%}<extra></extra>"),
    ))
    fig.update_layout(
        title=dict(text="Reliability diagram (test set)",
                   font=dict(size=13, color="#EDEFF7"), x=0, xanchor="left"),
        xaxis=dict(title=dict(text="Predicted churn probability",
                              font=dict(size=12, color=TEXT)),
                   range=[0, 1], tickformat=".0%",
                   tickfont=dict(size=12, color=TEXT),
                   gridcolor=GRID, zeroline=False),
        yaxis=dict(title=dict(text="Observed churn rate",
                              font=dict(size=12, color=TEXT)),
                   range=[0, 1], tickformat=".0%",
                   tickfont=dict(size=12, color=TEXT),
                   gridcolor=GRID, zeroline=False),
        legend=dict(font=dict(size=11, color=TEXT)),
        height=380,
        margin=dict(l=8, r=16, t=52, b=52),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#14141F", bordercolor="rgba(255,255,255,0.14)",
                        font=dict(size=12, color="#E8EAF2")),
    )
    return fig
