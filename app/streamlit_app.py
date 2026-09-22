"""IUL versus historical ETF investing: Streamlit entrypoint."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = next(p for p in APP.parents if (p / "fintools").is_dir())
for path in (ROOT, APP):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402
from market_data import load_daily  # noqa: E402
from model import DEFAULT_CHARGE, compare, month_ends  # noqa: E402
from views import render_compare, render_costs, render_method  # noqa: E402

from fintools.apps import query_choice, render_csv_download, sync_query_params  # noqa: E402

st.set_page_config(page_title="The $300 Question · IUL vs S&P 500", page_icon="◒", layout="wide")
st.markdown(f"<style>{(APP / 'styles.css').read_text()}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner=False)
def prices(ticker: str, offline: bool):
    return load_daily(ticker, offline=offline)


def qp_float(name, default, low, high):
    try:
        value = float(st.query_params.get(name, default))
        return value if low <= value <= high else default
    except (TypeError, ValueError):
        return default


def reset():
    for key in list(st.session_state):
        del st.session_state[key]
    st.query_params.clear()


if "initialized" not in st.session_state:
    st.session_state.update(
        initialized=True,
        ticker=query_choice("ticker", ["SPY", "VOO"], default="SPY"),
        budget=qp_float("budget", 300.0, 1.0, 100000.0),
        credit=qp_float("credit", 8.0, 0.0, 20.0),
        charge=qp_float("charge", DEFAULT_CHARGE, 0.0, 100000.0),
        view=query_choice(
            "view",
            ["The comparison", "Costs & coverage", "Method & data"],
            default="The comparison",
        ),
    )

with st.sidebar:
    st.markdown('<div class="eyebrow">◒ &nbsp; THE COMPOUND LAB</div>', unsafe_allow_html=True)
    st.header("Your comparison")
    st.caption("One monthly budget. Two different paths.")
    ticker = st.selectbox(
        "Historical ETF",
        ["SPY", "VOO"],
        key="ticker",
        format_func=lambda t: (
            "SPY · full 20-year history" if t == "SPY" else "VOO · history since 2010"
        ),
    )
    budget = st.number_input(
        "Monthly budget (USD)", min_value=1.0, max_value=100000.0, step=25.0, key="budget"
    )

with st.spinner("Loading verified market history…"):
    try:
        daily, meta = prices(ticker, os.environ.get("IUL_OFFLINE") == "1")
    except (ValueError, OSError) as exc:
        st.error(str(exc))
        st.info("Run the refresh_data.py script to install a verified historical snapshot.")
        st.stop()

now = pd.Timestamp.now(tz="America/New_York").tz_localize(None)
monthly = month_ends(daily, now)
if len(monthly) < 2:
    st.error("At least two completed months are required.")
    st.stop()
options = monthly.index.strftime("%Y-%m").tolist()
# Seed once, then preserve user choices across reruns; clamp on fund changes.
for key, default in (("end", options[-1]), ("start", options[max(0, len(options) - 240)])):
    if key not in st.session_state:
        candidate = st.query_params.get(key, default)
        st.session_state[key] = candidate if candidate in options else default
    elif st.session_state[key] not in options:
        st.session_state[key] = default

with st.sidebar:
    end = st.selectbox("Through month", options, key="end")
    starts = [x for x in options if x < end]
    if not starts:
        st.error("Select an endpoint with at least two months of history.")
        st.stop()
    if st.session_state.start not in starts:
        st.session_state.start = starts[max(0, len(starts) - 239)]
    start = st.selectbox("First monthly contribution", starts, key="start")
    if ticker == "VOO":
        st.caption("VOO launched in September 2010. No earlier returns are invented or spliced in.")
    with st.expander("IUL assumptions", expanded=True):
        credit = st.number_input(
            "Annual credited rate (%)", min_value=0.0, max_value=20.0, step=0.5, key="credit"
        )
        charge = st.number_input(
            "Implied monthly charges (USD)",
            min_value=0.0,
            max_value=100000.0,
            step=1.0,
            format="%.2f",
            key="charge",
        )
        st.caption(
            "Implied by the model; not verified policy fees. 8% is an effective annual assumption."
        )
    st.button("Reset comparison", on_click=reset, width="stretch")
    if st.button("Refresh market data", width="stretch"):
        prices.clear()
        st.rerun()
    st.caption("All values in USD · before personal taxes")

st.markdown(
    '<div class="eyebrow">INSURANCE & INVESTING / AN INTERACTIVE COMPARISON</div>',
    unsafe_allow_html=True,
)
st.title("The $300 question.")
st.markdown(
    '<div class="hero-copy">What could the same monthly budget have become? '
    "Compare historical S&P 500 investing with the advertised IUL example—"
    "and see the costs, protection and trade-offs behind the balances.</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="data-strip">● &nbsp; {ticker} · Yahoo Finance &nbsp; / &nbsp; '
    f"Last verified close {meta['last_observation']} &nbsp; / &nbsp; "
    f"{meta['status']} &nbsp; / &nbsp; Dividends reinvested</div>",
    unsafe_allow_html=True,
)
if meta.get("live_error"):
    st.warning(
        "Live refresh unavailable. Showing the dated, saved market history; no prices are estimated."
    )

view = st.radio(
    "Explore",
    ["The comparison", "Costs & coverage", "Method & data"],
    key="view",
    horizontal=True,
    label_visibility="collapsed",
)
sync_query_params(
    ticker=ticker, budget=budget, start=start, end=end, credit=credit, charge=charge, view=view
)
selected = monthly[
    (monthly.index.to_period("M") >= pd.Period(start))
    & (monthly.index.to_period("M") <= pd.Period(end))
]
try:
    result = compare(selected, budget, charge, credit / 100)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
context = dict(
    ticker=ticker,
    budget=budget,
    charge=charge,
    credit=credit / 100,
    monthly=selected,
    daily=daily,
    result=result,
    meta=meta,
    latest_window=end == options[-1],
)
if view == "The comparison":
    render_compare(**context)
elif view == "Costs & coverage":
    render_costs(**context)
else:
    render_method(**context)

st.markdown(
    '<div class="footer">Historical ETF backtest and a reconstructed IUL model. '
    "Neither guarantees future outcomes. Insurance protection and investment balances "
    "serve different purposes. The policy figures are user-reported; an actual insurer "
    "illustration is needed to verify them.</div>",
    unsafe_allow_html=True,
)
render_csv_download(
    result,
    label="Download this comparison · CSV",
    file_name=f"{ticker}_IUL_{start}_{end}.csv",
    key="main_csv",
)
