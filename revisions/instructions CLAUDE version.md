# Instructions CLAUDE version: IUL vs. historical S&P 500 investing (with index-linked line)

This version keeps every honesty constraint from `01-revised.md`, then adds a
second modeled IUL series — an **index-linked line** that runs the policy's
crediting mechanics (cap, floor, participation) over the real S&P 500 price
history — and reorganizes the whole thing as a phased build plan. Each phase
lists a goal, a concrete deliverable, its verification, and a ready-to-run
prompt.

## What changed from the revised brief

The revised brief modeled the IUL as a single smooth **flat-8%** line and
quarantined the cap/floor/participation formula into a standalone teaching
chart. That left two disconnected IUL stories. This version connects them:

- **IUL-A — advertised illustration (flat 8%).** Unchanged. A deterministic
  line reaching about $142,672. Labeled "advertised credited rate, hypothetical."
- **IUL-B — index-linked reconstruction (new).** Same premium, same implied
  charge, but the cash value is credited by applying the contract rule
  `max(floor, min(cap, participation × index_return − spread))` to the **real
  S&P 500 annual price return** at each policy anniversary. It shows caps
  clipping strong years, the floor holding flat in down years, and dividends
  excluded by construction. The old "index-credit mechanics" teaching chart now
  reads from the **same live parameters** as IUL-B, so the two views agree.

The point of IUL-B: it demonstrates, on data, why an advertised flat 8% is
usually optimistic. Real index crediting caps the upside and excludes
dividends, so IUL-B typically lands well below both the ETF and the IUL-A line.

## Non-negotiable honesty constraints (carried forward)

- ETF uses **actual historical total returns** (dividends reinvested), never an
  assumed 8%.
- IUL-B credits the **index price return only** (no dividends) — this is the
  real contract behavior and a core teaching contrast with the ETF.
- SPY is labeled "SPY — historical S&P 500 ETF proxy," never "VOO." No
  backfilling or splicing SPY prices into a VOO series.
- The 8% is a hypothetical assumption of unverified origin. Do not claim the
  insurer derived it from a 20-year S&P 500 average.
- The implied charge is a **fitted approximation**, not verified policy fees.
  Never recalibrate it to force every scenario to hit $142,672.
- Do not attribute the whole ETF-minus-IUL gap to fees: caps, dividend
  exclusion, forgone compounding and market returns all differ.
- No extrapolated prices or invented balances. Show a clear unavailable state
  when data are missing. Never label an older monthly value "today."
- This compares realized past ETF returns with modeled IUL series calibrated to
  a reported illustration — not two verified product outcomes. Past ≠ future.

---

# Model definitions

## Inputs and defaults

| Input | Default |
|---|---:|
| Monthly premium / ETF budget | $300 |
| Starting balances | $0 |
| Full comparison period | 240 monthly payments / 20 years |
| IUL-A effective annual credited rate, before charges | 8%, hypothetical |
| Equivalent constant monthly charge | $49.2579… (display $49.26) |
| Monthly cash-value contribution | $250.7421… (display $250.74) |
| Index-credit cap | 8% |
| Index-credit floor | 0% |
| Participation rate | 100% |
| Spread | 0% |
| User-reported 20-year illustrated account value | $142,672 |
| User-reported death benefit | $214,000; level coverage |

Display the charge as **$49.26** with the label "Implied by the model; not
verified policy fees." Keep full precision internally. Both IUL series use the
**same** monthly charge and $250.74 contribution, so they differ only in how the
cash value is credited.

## ETF (historical, total return)

Monthly total-return levels `A[t]` at actual month-end trading closes:

```text
ETF[t] = ETF[t−1] × (A[t] / A[t−1]) + monthly_budget
# Starting balance 0; first contribution earns returns only after purchase.
# Independent cross-check at valuation date T:
ETF[T] = sum(contribution[k] × A[T] / A[purchase_date[k]])
```

Assume fractional investing and dividend reinvestment; exclude personal taxes,
commissions and bid-ask spreads. Total-return series already embed fund
expenses — do not deduct an expense ratio again or add dividends twice.

## IUL-A — advertised flat-8% line (unchanged)

```text
m = (1 + iul_annual_credit)^(1/12) − 1
IUL_A[t] = IUL_A[t−1] × (1 + m) + premium − monthly_charge
```

Contributions and charges at month-end. At defaults, 240 periods give
**$142,672** from **$72,000 paid**: ~$11,822 implied charges, ~$60,178 net
contributions, ~$82,494 modeled growth.

## IUL-B — index-linked line (new)

Uses the **S&P 500 index price return** (no dividends), credited on an **annual
point-to-point** basis — the standard IUL crediting method.

```text
# Monthly: add the net contribution at month-end, no interim interest.
IUL_B[t] = IUL_B[t−1] + premium − monthly_charge

# On each 12-month policy anniversary, credit the whole balance:
index_return_12m = P[anniv] / P[anniv − 12] − 1        # price return, no dividends
credit_rate      = max(floor, min(cap, participation × index_return_12m − spread))
IUL_B[anniversary] = IUL_B[anniversary] × (1 + credit_rate)
```

- `P[·]` is the S&P 500 **price index** (recommend `^GSPC` month-end close), not
  a total-return series and not the ETF adjusted price.
- Crediting is **annual**, applied to the full balance at each anniversary. This
  is a simplification (real products credit per-segment on funds held a full
  term); label it "Modeled index crediting; simplified annual point-to-point."
- The "index-credit mechanics" teaching chart reads cap/floor/participation/
  spread from these **same controls** so the two views cannot diverge.
- Expected shape: caps clip strong years to `cap`, floor holds down years at
  `floor` (0%), dividends are absent — so IUL-B usually ends below IUL-A and
  well below the ETF. State this is the honest reconstruction of the mechanics,
  not a promise the insurer made.

## Term + ETF (optional)

Replace each ETF contribution with `budget − term_premium`. Leave insurance
inputs unset until supplied. Coverage must not silently extend past its term.
Never equate IUL charges with a term-insurance quote.

## Return on the full premium (context card)

From the full $300 outlay (not $250.74), solve `300 × factor(r, 240) = 142672`,
report `(1 + r)^12 − 1` ≈ **6.42%**, beside the advertised 8%. Recalculate on
input change; never hard-code. This excludes death protection, living benefits,
surrender charges and taxes.

---

# Build plan

## Phase 0 — Decide the delivery shape

- **Goal:** Lock the fact that a browser cannot run Python/yfinance, so all
  price data must be **baked into the page as JSON** at build time.
- **Deliverable:** One-line decision recorded here: single self-contained HTML
  page (Artifact) with an embedded `data.json` block; ~5,000 daily rows per
  series is small.
- **Verify:** No runtime network calls to price providers from the page.
- **Prompt:** "Confirm the page is a self-contained HTML artifact with prices
  embedded as JSON; no client-side data fetching."

## Phase 1 — Data snapshot and provenance

- **Goal:** Fetch and cache three series with the repo interpreter, not the
  browser: SPY total-return (adjusted close), VOO total-return (adjusted close),
  and `^GSPC` price close for IUL-B crediting.
- **Deliverable:** `data/prices.json` (daily and month-end), plus a
  `data/provenance.json` recording ticker, provider, coverage span, and UTC
  retrieval time. Use the repo's existing Yahoo/`fintools` loaders where they
  exist; add any new package to the correct requirements file first.
- **Verify:** SPY covers the full 20-year window; VOO starts no earlier than
  2010-09-07; `^GSPC` aligns to the same trading calendar; month-end samples sit
  on real trading closes.
- **Prompt:** "Using the repo interpreter, snapshot SPY and VOO adjusted-close
  total-return series and ^GSPC price close to data/prices.json with month-end
  samples, and write data/provenance.json with provider and retrieval time."

## Phase 2 — Pure calculation engine

- **Goal:** Implement ETF, IUL-A, IUL-B, term+ETF, drawdown, and
  return-on-premium as pure functions (JS in the page; optionally mirror in
  Python for the test harness).
- **Deliverable:** A `calc` module returning per-month series and headline
  scalars for any valid window and input set.
- **Verify:** See Phase 3.
- **Prompt:** "Implement the calc engine per the model definitions: ETF
  iterative + direct cross-check, IUL-A flat-8%, IUL-B annual point-to-point on
  ^GSPC price return, term+ETF, drawdown, and the 6.42% premium-return solve."

## Phase 3 — Verification harness (run before any UI)

- **Goal:** Assert the numbers before drawing anything.
- **Checks:**
  - Default window has 240 deposits and $72,000 paid in.
  - IUL-A checkpoints: $142,672 / ~$11,822 charges / ~$60,178 net / ~$82,494 growth.
  - Return-on-premium ≈ 6.4247%.
  - Zero-return balances equal net contributions (IUL) and total contributed (ETF).
  - Iterative and direct ETF results agree to cents.
  - IUL-B: a synthetic all-flat index credits `floor` every year; a synthetic
    +20%-every-year index credits `cap` every year; dividends never enter IUL-B.
  - Dividends and splits handled once; fund-inception and missing-data limits
    enforced; VOO recomputes IUL over the shorter window.
  - Latest-close valuation adds no premature deposit.
  - Guards: nonnegative budget and charge, charge within budget, valid term
    premium, cap ≥ floor.
  - The old assumed **$170,065 VOO value** and **$27,393 gap** are absent.
- **Prompt:** "Write and run the verification harness covering the checklist;
  do not build UI until every assertion passes."

## Phase 4 — Page shell and controls

- **Goal:** Layout, controls, dynamic headline, results cards.
- **Deliverable:** Controls for monthly budget, SPY/VOO history, valid date
  window, IUL-A rate + implied charge, and IUL-B cap/floor/participation/spread,
  with reset. No hypothetical ETF-return slider in historical mode. Results
  cards label each value "Historical ETF backtest," "IUL-A advertised
  illustration," or "IUL-B index-linked model."
- **Dynamic headline:** "Had you invested $[budget] each month in [ETF] from
  [first date] to [last date], your $[total contributed] would have been worth
  approximately $[value] as of [valuation date], with dividends reinvested,
  before personal taxes and trading costs." Every amount from verified data.
- **Verify:** Changing inputs updates headline and cards; window edges clamp to
  available data; VOO selector hides pre-inception dates.
- **Prompt:** "Build the responsive shell, controls (including IUL-B index
  parameters), reset, dynamic headline and labeled result cards."

## Phase 5 — Charts

| Chart | Required content |
|---|---|
| **Growth over time — primary** | ETF backtest, IUL-A (advertised), **IUL-B (index-linked)** and cumulative contributions on shared axes; optional term+ETF. ETF solid; IUL-A and IUL-B distinct dashed styles. Preserve market declines. Tooltips show dates, paid-in and balances. Note that only IUL-A's ending value was calibrated. |
| **Historical drawdowns — below growth** | Daily ETF total-return drawdown `A[t]/running_max(A)[t] − 1`; worst decline in window; contribution-free series. State that smooth IUL curves are not evidence of zero policy risk. |
| **Where the money goes — secondary** | $300 split into $49.26 implied charge + $250.74 contribution, tagged "Implied by the model; not verified policy fees." Separate ending-value breakdowns. Do not label the full ETF gap as fees. |
| **Money available on exit — secondary** | ETF value and modeled IUL account value; surrender value only when a real schedule is supplied (`max(0, account − charge)`, before taxes), labeled "Modeled surrender value; not insurer-verified." Otherwise "Policy surrender schedule required." |
| **Index-credit mechanics — expandable** | Price returns −30%…+30% through `max(floor, min(cap, participation × r − spread))`, **reading the live IUL-B controls**. Explains exactly how IUL-B's yearly credits are formed. |

- **Prompt:** "Build the five charts; add the IUL-B line to the growth chart and
  wire the index-credit mechanics chart to the same cap/floor/participation
  controls."

## Phase 6 — Explanations, disclosure, accessibility, export

- **Goal:** Short expandable explanations, data provenance, disclosures, mobile
  controls, data-table alternatives, CSV export, and a tax note.
- **Essential explanations:** permanent-insurance funding risk; 0% floor does
  not stop charge-driven cash-value loss; surrender can leave proceeds below
  premiums and ends coverage; level $214,000 benefit is not benefit-plus-cash;
  ETF alone has no insurance; term+ETF is temporary protection. **Add a tax
  panel** (unmodeled): tax-deferred cash value, generally income-tax-free death
  benefit and policy loans vs. taxable ETF gains — so the "before taxes" ETF
  figure understates the IUL's tax edge; surface it rather than hide it.
- **Disclosure:** "Historical ETF backtest and modeled IUL illustrations
  (advertised flat rate and index-linked reconstruction). Neither guarantees
  future outcomes."
- **Verify:** Accessible labels, keyboard reachable, CSV matches on-screen
  series, valuation dates shown beside results.
- **Prompt:** "Add explanations, the tax panel, provenance and disclosure block,
  data tables and CSV export; check accessibility."

## Phase 7 — Final QA

- **Goal:** Re-run Phase 3 assertions inside the finished page, confirm all IUL
  outputs keep their model labels, and spot-check VOO and a shorter window.
- **Prompt:** "Re-run verification in the built page and confirm labels,
  disclosures and the VOO shorter-window recalculation."

---

# Sources

Fund inception facts checked 2026-09-22. Add the chosen historical-data source
and retrieval date when implementing. The user's policy figures remain
unverified until the actual illustration is supplied.

- [Vanguard: VOO fact sheet, inception and total-return conventions](https://fund-docs.vanguard.com/F0968.pdf)
- [State Street: SPY inception and fund information](https://www.ssga.com/us/en/institutional/etfs/state-street-spdr-sp-500-etf-trust-spy)
- [NAIC: Life insurance illustrations](https://content.naic.org/insurance-topics/life-insurance-illustrations)
- [New York DFS: Universal life mechanics and charges](https://www.dfs.ny.gov/consumers/life_insurance)
- [FINRA: Surrender charges and policy exchanges](https://www.finra.org/investors/insights/should-you-exchange-your-life-insurance-policy)
