"""Pure monthly accumulation and historical total-return calculations."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

DEFAULT_CHARGE = 49.25793780551214
IUL_LABEL = "Reconstructed IUL model (USD)"
ETF_LABEL = "Historical ETF backtest (USD)"
TERM_LABEL = "Term + historical ETF (USD)"
PAID_LABEL = "Total contributed (USD)"


def factor(rate: float, months: int) -> float:
    if months < 1 or rate <= -1 or not math.isfinite(rate):
        raise ValueError("Use positive months and a finite monthly rate above -100%.")
    if abs(rate) < 1e-12:
        return float(months)
    return math.expm1(months * math.log1p(rate)) / rate


def premium_return(payment: float, months: int, ending: float) -> float | None:
    """Periodic cash-flow IRR, annualized; final deposit and balance share a date."""
    if payment <= 0 or months < 2 or ending <= payment or not math.isfinite(ending):
        return None
    target = ending / payment
    low, high = -0.999999999, 1.0
    if factor(high, months) < target:
        return None
    for _ in range(100):
        middle = (low + high) / 2
        if factor(middle, months) < target:
            low = middle
        else:
            high = middle
    return math.expm1(12 * math.log1p((low + high) / 2))


def month_ends(daily: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Keep completed calendar months and actual last trading dates."""
    work = daily.sort_index().copy()
    periods = work.index.to_period("M")
    work = work[periods < pd.Timestamp(as_of).to_period("M")]
    rows = work.groupby(work.index.to_period("M")).tail(1)
    # A partial tail must never be mistaken for a completed month.
    rows = rows[rows.index.day >= rows.index.days_in_month - 4]
    return rows


def compare(
    monthly: pd.DataFrame,
    budget: float,
    charge: float,
    annual_credit: float,
    term_premium: float | None = None,
    term_months: int = 0,
) -> pd.DataFrame:
    values = [budget, charge, annual_credit]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Enter finite assumptions.")
    if budget <= 0 or not 0 <= charge <= budget or not 0 <= annual_credit <= 1:
        raise ValueError(
            "Use a positive budget, charges within it and an IUL rate from 0% to 100%."
        )
    if term_premium is not None and (
        not math.isfinite(term_premium) or not 0 <= term_premium <= budget or term_months < 1
    ):
        raise ValueError(
            "Term premiums must fit the budget and coverage must last at least a month."
        )
    if monthly.empty or monthly.index.has_duplicates or not monthly.index.is_monotonic_increasing:
        raise ValueError("Select a nonempty, ordered monthly window.")
    periods = monthly.index.to_period("M").astype("int64")
    if len(periods) > 1 and not np.all(np.diff(periods) == 1):
        raise ValueError("The selected historical window has missing months.")
    prices = monthly["Adjusted close"].to_numpy(dtype=float)
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("Historical adjusted prices must be finite and positive.")
    m = (1 + annual_credit) ** (1 / 12) - 1
    etf, iul, term = 0.0, 0.0, 0.0
    records = []
    for i, price in enumerate(prices):
        growth = price / prices[i - 1] if i else 1.0
        etf = etf * growth + budget
        iul = iul * (1 + m) + budget - charge
        row = {PAID_LABEL: budget * (i + 1), ETF_LABEL: etf, IUL_LABEL: iul}
        if term_premium is not None:
            premium = term_premium if i < term_months else 0
            term = term * growth + budget - premium
            row[TERM_LABEL] = term
            row["Term coverage active"] = i < term_months
        records.append(row)
    result = pd.DataFrame(records, index=monthly.index)
    result.index.name = "Date"
    direct = (budget * prices[-1] / prices).sum()
    if not np.isclose(etf, direct, rtol=1e-10):
        raise ArithmeticError("Historical accumulation cross-check failed.")
    return result


def drawdown(daily: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    prices = daily.loc[start:end, "Adjusted close"]
    return (prices / prices.cummax() - 1).rename("ETF drawdown (%)") * 100


def apply_surrender(result: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    """Only explicitly supplied dates, no interpolation or assumed zero fees."""
    required = {"Date", "Surrender charge (USD)"}
    if not required <= set(schedule):
        raise ValueError("CSV needs Date and Surrender charge (USD) columns.")
    work = schedule[list(sorted(required))].copy()
    work["Date"] = pd.to_datetime(work["Date"], errors="raise").dt.normalize()
    work["Surrender charge (USD)"] = pd.to_numeric(work["Surrender charge (USD)"], errors="raise")
    if work["Date"].duplicated().any():
        raise ValueError("Use each date once.")
    charges = work["Surrender charge (USD)"]
    if not np.isfinite(charges).all() or (charges < 0).any():
        raise ValueError("Surrender charges must be finite and nonnegative.")
    merged = result.join(work.set_index("Date"), how="inner")
    if merged.empty:
        raise ValueError("Supply dates matching the contribution dates in the downloaded table.")
    merged["Modeled surrender value; not insurer-verified (USD)"] = (
        merged[IUL_LABEL] - merged["Surrender charge (USD)"]
    ).clip(lower=0)
    return merged


def validate_illustration(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["Date", "Account value (USD)", "Cash surrender value (USD)", "Guarantee status"]
    if not set(required) <= set(frame):
        raise ValueError("Use the four columns shown in the illustration template.")
    work = frame[required].copy()
    work["Date"] = pd.to_datetime(work["Date"], errors="raise").dt.normalize()
    if work["Date"].duplicated().any() or work["Date"].isna().any():
        raise ValueError("Provide one valid dated illustration value per row.")
    for col in required[1:3]:
        work[col] = pd.to_numeric(work[col], errors="raise")
        if not np.isfinite(work[col]).all() or (work[col] < 0).any():
            raise ValueError("Illustrated account and surrender values must be nonnegative.")
    if not work["Guarantee status"].isin(["Guaranteed", "Non-guaranteed"]).all():
        raise ValueError("Guarantee status must be Guaranteed or Non-guaranteed.")
    return work.sort_values("Date")
