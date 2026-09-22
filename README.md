# IUL vs. Direct Investing

An honest, data-backed comparison: what $300 a month would have become in an
S&P 500 ETF, next to an indexed universal life (IUL) illustration.

The ETF side uses **actual historical total returns** (dividends reinvested).
The IUL is modeled two ways:

- **IUL-A — advertised illustration:** a flat 8% effective-annual credited rate,
  fitted once to a reported $142,672 ending value, then held fixed.
- **IUL-B — index-linked reconstruction:** the same premium and charge, but the
  cash value is credited by applying the contract rule
  `max(floor, min(cap, participation × index_return − spread))` to the **real
  S&P 500 price index** (dividends excluded), annual point-to-point.

IUL-B shows, on data, why an advertised flat 8% is usually optimistic: caps clip
strong years, the floor holds down years flat, and dividends never accrue.

## Layout

- `IUL-vs-index-investing.md` — original brief.
- `revisions/` — brief revisions and two build-instruction variants
  (`instructions CLAUDE version.md`, `instructions GPT version.md`).
- `app/calc.js` — the calculation engine (single source of truth, tested).
- `app/template.html` — page markup, styles and UI glue.
- `app/index.html` — the built, self-contained page (open directly in a browser).
- `app/` also contains an earlier Streamlit version of the tool.
- `data/prices.json` — cached price snapshot; `data/provenance.json` — provider
  and retrieval record.
- `scripts/` — data snapshot, verification harness, and page build.

## Rebuild and verify

```bash
# 1. refresh the price snapshot (needs pandas + yfinance)
python scripts/snapshot_prices.py

# 2. run the verification harness (Node)
node scripts/verify.mjs

# 3. build the self-contained page
node scripts/build_page.mjs   # -> app/index.html
```

## Data and disclosure

Prices via Yahoo Finance (yfinance). ETF series use adjusted close (total
return); the IUL-B index uses the S&P 500 price close (dividends excluded).
Historical ETF backtest and modeled IUL illustrations — neither guarantees
future outcomes. Policy figures are user-reported and unverified.
