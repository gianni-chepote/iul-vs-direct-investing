"""Yahoo daily adjusted prices, with an explicitly dated real-data fallback."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

FIXTURES = Path(__file__).parent / "fixtures"
SYMBOLS = {"SPY": "1993-01-22", "VOO": "2010-09-07"}


def validate(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy().sort_index()
    if frame.empty or frame.index.has_duplicates or len(frame) < 200:
        raise ValueError("Insufficient or duplicate daily history.")
    for col in ("Close", "Adjusted close"):
        if col not in frame or not np.isfinite(frame[col]).all() or (frame[col] <= 0).any():
            raise ValueError("Missing or invalid historical prices.")
    if frame.index.to_series().diff().dropna().dt.days.max() > 7:
        raise ValueError("History is not a continuous daily trading series.")
    frame.index.name = "Date"
    return frame


def fetch_daily(ticker: str) -> tuple[pd.DataFrame, dict]:
    if ticker not in SYMBOLS:
        raise ValueError("Choose SPY or VOO.")
    now = datetime.now(UTC)
    start = int(pd.Timestamp(SYMBOLS[ticker], tz="UTC").timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    response = requests.get(
        url,
        params={
            "period1": start,
            "period2": int(now.timestamp()),
            "interval": "1d",
            "events": "div,splits",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    raw = response.json()["chart"]["result"][0]
    if raw["meta"].get("dataGranularity") != "1d":
        raise ValueError("Provider did not return daily data.")
    quotes = raw["indicators"]["quote"][0]
    adjusted = raw["indicators"]["adjclose"][0]["adjclose"]
    dates = (
        pd.to_datetime(raw["timestamp"], unit="s", utc=True)
        .tz_convert("America/New_York")
        .tz_localize(None)
        .normalize()
    )
    frame = pd.DataFrame({"Close": quotes["close"], "Adjusted close": adjusted}, index=dates)
    local_now = now.astimezone(ZoneInfo("America/New_York"))
    today = pd.Timestamp(local_now.date())
    # Exclude the current day's partial quote until after the regular session.
    cutoff = (
        today if (local_now.hour, local_now.minute) >= (16, 15) else today - pd.Timedelta(days=1)
    )
    frame = validate(frame.loc[frame.index <= cutoff])
    meta = {
        "ticker": ticker,
        "provider": "Yahoo Finance",
        "source_url": url,
        "retrieved_utc": now.isoformat(),
        "first_observation": str(frame.index.min().date()),
        "last_observation": str(frame.index.max().date()),
        "rows": len(frame),
        "adjustment": "Provider Adjusted Close: split- and dividend-adjusted; expenses embedded.",
        "status": "Live retrieval",
        "live_error": None,
    }
    return frame, meta


def load_daily(ticker: str, *, offline: bool = False) -> tuple[pd.DataFrame, dict]:
    error = None
    if not offline:
        try:
            return fetch_daily(ticker)
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            error = type(exc).__name__
    path = FIXTURES / f"{ticker}.csv"
    if not path.exists():
        raise ValueError("Historical prices are unavailable; no verified snapshot is installed.")
    frame = validate(pd.read_csv(path, parse_dates=["Date"], index_col="Date"))
    meta = json.loads((FIXTURES / f"{ticker}.json").read_text())
    meta.update(status="Saved real-data snapshot", live_error=error)
    return frame, meta


def save_snapshot(ticker: str) -> dict:
    frame, meta = fetch_daily(ticker)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    frame.to_csv(FIXTURES / f"{ticker}.csv", float_format="%.10f")
    (FIXTURES / f"{ticker}.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta
