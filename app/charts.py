"""Interactive charts with explicit historical/model distinctions."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from model import ETF_LABEL, IUL_LABEL, PAID_LABEL, TERM_LABEL

from fintools.apps import apply_app_plotly_theme

TEAL = "#13776c"
ORANGE = "#c37b3e"
MUTED = "#9b9c92"
INK = "#203832"


def style(fig: go.Figure, *, height: int = 430, money: bool = True, time: bool = True) -> go.Figure:
    apply_app_plotly_theme(
        fig,
        yaxis_title="Account value · USD" if money else None,
        height=height,
        range_selector=False,
        range_slider=False,
    )
    fig.update_layout(
        paper_bgcolor="#fffefb",
        plot_bgcolor="#fffefb",
        font=dict(family="Arial", color=INK),
        margin=dict(l=12, r=15, t=55, b=25),
        legend=dict(x=0, xanchor="left", y=1.04, yanchor="bottom", font=dict(size=11)),
    )
    fig.update_yaxes(gridcolor="#e9ece6", tickprefix="$" if money else "", automargin=True)
    if not time:
        fig.update_xaxes(tickformatstops=[], rangeslider_visible=False)
    return fig


def growth(frame: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()
    for col, label, color, dash in [
        (ETF_LABEL, f"{ticker} · historical", TEAL, "solid"),
        (IUL_LABEL, "Reconstructed IUL model", ORANGE, "dash"),
        (PAID_LABEL, "Total contributed", MUTED, "dot"),
        (TERM_LABEL, f"Term + {ticker} · historical", "#5d6891", "solid"),
    ]:
        if col in frame:
            fig.add_trace(
                go.Scatter(
                    x=frame.index,
                    y=frame[col],
                    mode="lines",
                    name=label,
                    line=dict(color=color, width=3 if col == ETF_LABEL else 2, dash=dash),
                    hovertemplate="%{y:$,.0f}<extra>%{fullData.name}</extra>",
                )
            )
    return style(fig)


def drawdowns(series: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=series.index,
            y=series,
            fill="tozeroy",
            mode="lines",
            line=dict(color="#aa7257", width=1.4),
            fillcolor="rgba(170,114,87,.12)",
            name="ETF drawdown",
            hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra></extra>",
        )
    )
    style(fig, height=220, money=False)
    fig.update_layout(margin=dict(l=10, r=15, t=12, b=20))
    fig.update_yaxes(
        ticksuffix="%", title="Below prior peak", range=[min(series.min() * 1.15, -1), 1]
    )
    return fig


def allocation(budget: float, charge: float) -> go.Figure:
    fig = go.Figure()
    for name, value, color in [
        ("Net cash-value contribution", budget - charge, TEAL),
        ("Implied charges · not verified", charge, ORANGE),
    ]:
        fig.add_trace(
            go.Bar(
                x=[value],
                y=["Monthly premium"],
                orientation="h",
                name=name,
                marker_color=color,
                text=[f"${value:,.2f}"],
                textposition="inside",
                hovertemplate="%{x:$,.2f}<extra>%{fullData.name}</extra>",
            )
        )
    style(fig, height=190, money=False, time=False)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="USD per month", tickprefix="$")
    return fig


def mechanics(cap: float, participation: float, spread: float) -> go.Figure:
    x = np.linspace(-30, 30, 121)
    y = np.maximum(0, np.minimum(cap, participation / 100 * x - spread))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x, y=x, name="Index price return", line=dict(color=MUTED, dash="dot"))
    )
    fig.add_trace(
        go.Scatter(x=x, y=y, name="Illustrative IUL credit", line=dict(color=ORANGE, width=3))
    )
    style(fig, height=300, money=False, time=False)
    fig.update_xaxes(title="Index price return", ticksuffix="%")
    fig.update_yaxes(title="Annual credited interest", ticksuffix="%")
    return fig
