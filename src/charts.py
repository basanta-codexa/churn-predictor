"""Plotly figures for the churn application.

Plotly is used instead of Matplotlib so the charts remain responsive and
readable at different viewport widths. All figures share the same neutral
palette and typography as the rest of the interface.
"""
from __future__ import annotations

import plotly.graph_objects as go

RED = "#F87171"
BLUE = "#7C8CFF"
GREY = "#8B90A0"
TEXT = "#E6E8EE"
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
            text=("Contribution to churn probability"
                  f"<br><sup>customer {final_p:.0%} · "
                  f"model baseline {base_p:.0%}</sup>"),
            font=dict(size=14, color=TEXT),
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
        font=dict(family="Segoe UI, Arial, sans-serif", color=TEXT),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#14171F", bordercolor="#333A4A",
                        font=dict(size=12, color=TEXT)),
    )

    # population baseline and where this customer ends up
    fig.add_vline(x=base_p, line=dict(color=GREY, width=1, dash="dash"),
                  layer="below")
    fig.add_vline(x=final_p, line=dict(color=TEXT, width=1.5), layer="below")
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
        title=dict(text="SHAP attribution (log-odds)",
                   font=dict(size=14, color=TEXT), x=0, xanchor="left"),
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
        font=dict(family="Segoe UI, Arial, sans-serif", color=TEXT),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#14171F", bordercolor="#333A4A",
                        font=dict(size=12, color=TEXT)),
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
    predicted = curve["predicted"]
    actual = curve["actual"]
    counts = curve.get("counts")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration",
        line=dict(color=GREY, width=1, dash="dash"),
        hoverinfo="skip",
    ))

    marker = dict(size=8, color=RED, line=dict(width=1, color="#0B0D12"))
    hover = "Predicted %{x:.1%}<br>Observed %{y:.1%}<extra></extra>"
    if counts and len(counts) == len(predicted):
        peak = max(counts) or 1
        marker["size"] = [
            max(6, min(18, 6 + 12 * (count / peak) ** 0.5))
            for count in counts
        ]
        hover = ("Predicted %{x:.1%}<br>Observed %{y:.1%}"
                 "<br>n = %{customdata}<extra></extra>")

    fig.add_trace(go.Scatter(
        x=predicted, y=actual, mode="lines+markers",
        name="Model",
        line=dict(color=RED, width=2),
        marker=marker,
        customdata=counts,
        hovertemplate=hover,
    ))
    fig.update_layout(
        title=dict(text="Calibration on the held-out test set",
                   font=dict(size=13, color=TEXT), x=0, xanchor="left"),
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
        hoverlabel=dict(bgcolor="#14171F", bordercolor="#333A4A",
                        font=dict(size=12, color=TEXT)),
    )
    return fig
