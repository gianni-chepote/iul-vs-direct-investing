"""Phase 1 data snapshot for the IUL vs. direct-investing webpage.

Fetches three series with the repo interpreter (a browser cannot), and writes a
self-contained JSON payload plus a provenance record:

- SPY total-return series (dividend- and split-adjusted close) -> ETF backtest.
- VOO total-return series (adjusted close)                     -> ETF alternative.
- ^GSPC price close (dividends excluded)                       -> IUL-B index credits.

Convention: auto_adjust=False, then use "Adj Close" for the ETFs (total return,
dividends reinvested and splits handled) and "Close" for ^GSPC (price index, no
dividends). The default endpoint is the last completed calendar month.

Run: ./.venv/bin/python "fins2026/IUL vs Direct Investing/scripts/snapshot_prices.py"
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Last completed calendar month relative to today (2026-09-22 -> 2026-08-31).
TODAY = pd.Timestamp.today().normalize()
LAST_COMPLETED_MONTH_END = (TODAY.replace(day=1) - pd.Timedelta(days=1)).normalize()

PROVIDER = "Yahoo Finance via yfinance"


def _series(df: pd.DataFrame, column: str) -> pd.Series:
    """Extract one price column as a clean, date-indexed float series."""
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance returns a MultiIndex when given a single ticker in a list.
        df = df.droplevel(1, axis=1)
    s = df[column].dropna()
    s = s[s.index <= LAST_COMPLETED_MONTH_END]
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    return s.astype(float)


def _records(s: pd.Series, value_name: str) -> list[dict]:
    return [{"date": d.strftime("%Y-%m-%d"), value_name: round(float(v), 6)}
            for d, v in s.items()]


def _month_end(s: pd.Series) -> pd.Series:
    """Last available trading close in each calendar month."""
    return s.groupby([s.index.year, s.index.month]).tail(1)


def fetch(ticker: str, price_column: str) -> pd.Series:
    raw = yf.download(
        ticker,
        period="max",
        interval="1d",
        auto_adjust=False,
        actions=False,
        progress=False,
    )
    if raw.empty:
        raise SystemExit(f"No data returned for {ticker}")
    return _series(raw, price_column)


def main() -> None:
    retrieved = datetime.now(timezone.utc).isoformat()

    spy = fetch("SPY", "Adj Close")   # total return
    voo = fetch("VOO", "Adj Close")   # total return
    gspc = fetch("^GSPC", "Close")    # price index, no dividends

    payload = {
        "meta": {
            "provider": PROVIDER,
            "retrieved_utc": retrieved,
            "last_completed_month_end": LAST_COMPLETED_MONTH_END.strftime("%Y-%m-%d"),
            "conventions": {
                "spy": "adjusted close (total return; dividends reinvested, splits handled)",
                "voo": "adjusted close (total return; dividends reinvested, splits handled)",
                "gspc": "close (S&P 500 price index; dividends excluded, used for IUL-B credits)",
            },
        },
        # ETFs: keep daily (for the drawdown chart) and month-end (for contributions).
        "spy": {
            "daily": _records(spy, "adj_close"),
            "monthly": _records(_month_end(spy), "adj_close"),
        },
        "voo": {
            "daily": _records(voo, "adj_close"),
            "monthly": _records(_month_end(voo), "adj_close"),
        },
        # Index credits are annual point-to-point, so month-end levels suffice.
        "gspc": {
            "monthly": _records(_month_end(gspc), "close"),
        },
    }

    provenance = {
        "provider": PROVIDER,
        "retrieved_utc": retrieved,
        "last_completed_month_end": LAST_COMPLETED_MONTH_END.strftime("%Y-%m-%d"),
        "series": {
            "SPY": {
                "role": "ETF total-return backtest",
                "column": "Adj Close",
                "coverage_start": spy.index.min().strftime("%Y-%m-%d"),
                "coverage_end": spy.index.max().strftime("%Y-%m-%d"),
                "n_daily": int(spy.size),
                "n_monthly": int(_month_end(spy).size),
            },
            "VOO": {
                "role": "ETF total-return alternative",
                "column": "Adj Close",
                "coverage_start": voo.index.min().strftime("%Y-%m-%d"),
                "coverage_end": voo.index.max().strftime("%Y-%m-%d"),
                "n_daily": int(voo.size),
                "n_monthly": int(_month_end(voo).size),
            },
            "^GSPC": {
                "role": "S&P 500 price index for IUL-B annual point-to-point credits",
                "column": "Close",
                "coverage_start": gspc.index.min().strftime("%Y-%m-%d"),
                "coverage_end": gspc.index.max().strftime("%Y-%m-%d"),
                "n_monthly": int(_month_end(gspc).size),
            },
        },
    }

    (DATA_DIR / "prices.json").write_text(json.dumps(payload, separators=(",", ":")))
    (DATA_DIR / "provenance.json").write_text(json.dumps(provenance, indent=2))

    print("Wrote", DATA_DIR / "prices.json")
    print("Wrote", DATA_DIR / "provenance.json")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
