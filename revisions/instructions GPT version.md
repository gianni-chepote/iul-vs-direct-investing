# Instructions GPT version: IUL vs. historical S&P 500 investing

## Goal

Build a responsive, interactive webpage answering: **“If you had invested $300 each month in an S&P 500 ETF, what would it be worth by the selected date, compared with this advertised IUL illustration?”** Explain growth, costs, liquidity, drawdowns and insurance protection through charts and short explanations. Use USD and a U.S. product context.

Keep the IUL's advertised **8% annual credited rate** as a hypothetical assumption; treating it as an effective annual rate is our modeling convention, not a verified contract term. Its origin is unverified: do not claim the insurer derived it from a 20-year S&P 500 average. The ETF side must use actual historical total returns, including reinvested dividends, rather than assuming 8% every year.

## Historical period and investment choice

- **Default: 20-year S&P 500 ETF history using SPY.** SPY launched in January 1993 and covers the full window. Label it “SPY — historical S&P 500 ETF proxy,” never “20-year VOO performance.” SPY and VOO have different expenses and tracking results.
- **Alternative: actual VOO history.** VOO launched on September 7, 2010. Restrict its selector to available trading data; do not backfill or splice earlier SPY prices into a series called VOO. Recalculate the IUL and contributions over the same shorter period.
- Use the latest **completed calendar month** with verified data as the default endpoint. For example, an August 31, 2026 endpoint uses 240 deposits from September 2006 through August 2026. Buy at the last trading close of each month. Specify the actual start, end and contribution dates.
- Add an optional **“Value at latest available close”** readout: carry the final month-end ETF balance forward using the observed total-return factor, without adding a contribution for the unfinished month. Identify the U.S. close date and data retrieval time. Never label an older monthly value “today.”
- No extrapolated prices or invented historical balances. If data are unavailable, show the last verified date or a clear unavailable state.

## Page flow and controls

1. **Introduction:** “Where would your $300 a month have taken you?” Explain that IUL combines insurance and cash value; an ETF owns investments tracking a large-cap U.S. index without providing life insurance.
2. **Controls:** Monthly budget, SPY/VOO history, valid date window, IUL credited rate and equivalent monthly charge. Include reset. Do not expose a hypothetical ETF return slider in historical mode.
3. **Results:** Total contributed, historical ETF ending value, ETF gain/loss, reconstructed IUL value and difference. Label each result “Historical ETF backtest” or “Reconstructed IUL model.” Show the advertised 8% credit beside the approximately 6.42% cash-value-equivalent return on the full premiums; explain the distinction below.
4. **Dynamic headline:** “Had you invested $[budget] each month in [ETF] from [first contribution date] to [last contribution date], your $[total contributed] would have been worth approximately $[value] as of [valuation date], with dividends reinvested, before personal taxes and trading costs.” Populate every amount from verified data.
5. **Optional term insurance + ETF:** Accept a user-entered term premium, coverage amount and term duration; invest the remaining budget. Leave insurance inputs unset until supplied. Coverage must not silently extend past its term. Never equate IUL charges with a term-insurance quote.
6. **Visual hierarchy:** Lead with the growth chart, total contributions and ending balances. Put historical drawdowns immediately below. Keep allocation and liquidity details secondary; put index-credit mechanics, formulas and data provenance in expandable panels. Do not give all five charts equal prominence.

## Reconstructed IUL assumptions and model

| Input | Default |
|---|---:|
| Monthly premium / ETF budget | $300 |
| Starting balances | $0 |
| Full comparison period | 240 monthly payments / 20 years |
| IUL effective annual credited rate, before charges | 8%, hypothetical |
| Equivalent constant monthly charge | $49.25793780551214 |
| Monthly cash-value contribution | $250.74206219448786 |
| User-reported 20-year illustrated account value | $142,672 |
| User-reported death benefit | $214,000; assume level coverage |

Display charges as **$49.26**, with the adjacent label **“Implied by the model; not verified policy fees.”** Keep full precision internally. The charge was fitted to one reported ending value; it does not establish the insurer's actual fees or account balances in years 1–19. Keep the charge fixed when changing scenario inputs; do not force every scenario to reach $142,672.

Use **“Reconstructed IUL model”** in chart legends, tooltips, cards and exports. If the insurer's annual illustration becomes available, provide a separate **“Insurer-provided illustrated values”** series and identify guaranteed versus non-guaranteed columns. Those projections are still not historical policy performance. Do not silently interpolate between supplied years; label any interpolation as modeled.

The interest convention affects the fitted charge: an 8% **effective annual** rate implies approximately **$49.26/month**, while 8% **nominal annual interest compounded monthly** implies approximately **$57.78/month** for the same target. Present this as a sensitivity example in the methodology panel, not a second verified fee quotation. For either convention, `implied_charge = 300 − 142672 / factor(monthly_rate, 240)`; the default convention remains effective annual.

```text
m = (1 + iul_annual_credit)^(1/12) − 1
IUL[t] = IUL[t−1] × (1 + m) + premium − monthly_charge
```

Apply contributions and charges at month-end in this simplified model. At default inputs, 240 periods yield **$142,672** from **$72,000 paid**, approximately **$11,822 in implied charges**, **$60,178 in net contributions** and **$82,494 in modeled growth**. Recalculate for shorter windows; do not compare 16 years of ETF investing with 20 years of IUL funding.

The optional latest-close IUL readout can accrue the last month-end balance at `(1 + annual_credit)^(elapsed_calendar_days / 365.25)` with no new payment or charge before the next scheduled month-end. Disclose that day-count convention and retain the “Reconstructed IUL model” label.

## Return on the full premium

Add a small comparison beside the IUL result:

> **Advertised credited rate: 8%** · **Cash-value-equivalent annual return on premiums: approximately 6.42%**

Calculate the second rate from the full **$300 monthly outlay**, not the $250.74 remaining after assumed charges. For the default 240 month-end payments and final account value of $142,672, solve:

```text
factor(r, n) = ((1 + r)^n − 1) / r
factor(0, n) = n
300 × factor(r, 240) = 142672
cash_value_equivalent_annual_return = (1 + r)^12 − 1
# Default result: approximately 6.424675%.
```

Explain: “The 8% applies to the model's cash-value growth before monthly charges. The 6.42% expresses the ending account value relative to all premiums paid.” This is not a measure of the total value of insurance: it excludes death protection and living benefits, and uses account value before any surrender charges or personal taxes. Actual exit proceeds could imply a lower return.

Recalculate this metric when scenario inputs change; do not hard-code 6.42%. Support zero and negative returns when mathematically defined, and show “Not available” when a valid finite rate cannot be calculated. If displaying an ETF contribution-based return beside it, use the same cash-flow timing convention; do not substitute a lump-sum CAGR.

## Historical ETF calculation and data

Use a reliable daily **total-return series or dividend- and split-adjusted closing prices**, with documented adjustment conventions. Cache the retrieved dataset and record ticker, provider, coverage and retrieval time. Use issuer sources to verify fund identity and benchmark performance, and a documented historical-data provider for the calculation. Do not use raw S&P 500 price levels as if they included dividends.

For monthly total-return levels `A[t]` sampled at actual month-end trading closes:

```text
ETF[t] = ETF[t−1] × (A[t] / A[t−1]) + monthly_budget
# Starting balance is zero; first contribution earns returns only after purchase.
# Independent cross-check at valuation date T:
ETF[T] = sum(contribution[k] × A[T] / A[purchase_date[k]])
```

For term + ETF, replace each contribution with the budget minus the applicable term premium. Assume fractional investing and dividend reinvestment; exclude personal taxes, commissions and bid-ask spreads. Historical ETF total returns already incorporate fund expenses: **do not deduct today's expense ratio again or add dividends twice**. Adjusted-price units are calculation units, not actual shares purchased at raw market prices.

Show any historical CAGR as context only. Monthly contributions experience different holding periods; neither a simple arithmetic average nor a constant CAGR reproduces their actual investment outcome. Do not apply historical total returns directly to IUL credits: real policy caps, participation rates, dividend exclusions, charges and crediting dates differ.

## Charts

| Chart | Required content |
|---|---|
| **Growth over time — primary** | Historical ETF backtest, reconstructed IUL balance and cumulative contributions on shared axes; optional term + ETF. Use solid historical and dashed modeled lines. State near the chart that only the IUL ending value was used for calibration; intermediate balances are not verified policy values. Preserve market declines. Tooltips show dates, paid-in amounts and balances. |
| **Historical drawdowns — directly below growth** | Daily ETF total-return drawdown: `A[t] / running_max(A)[t] − 1`. Show the worst observed decline in the selected period. Use the contribution-free return series so deposits cannot disguise losses. A smooth reconstructed IUL curve is not evidence of zero policy risk. |
| **Where the money goes — secondary** | Monthly $300 premium split into $49.26 implied charges and $250.74 cash-value contribution; separate ending-value breakdowns. Put “Implied by the model; not verified policy fees” on the chart itself. Explain that insurance charges buy coverage. Do not label the historical ending-value gap entirely as fees: market returns and forgone compounding also differ. |
| **Money available on exit — secondary** | Show historical ETF value and the reconstructed IUL account value. Display insurer-provided surrender values only when the corresponding illustration is supplied, with guarantee status identified. A surrender-charge schedule alone does not verify the underlying account value: if applied to the reconstructed curve, label the result “Modeled surrender value; not insurer-verified.” With no loans, use `max(0, modeled_account_value − supplied_surrender_charge)`, before taxes. Without the necessary schedule, show “Policy surrender information required”; never assume zero charges. |
| **Index-credit mechanics — expandable** | A separate teaching chart using price returns from −30% to +30%, floor 0%, cap 8%, participation 80%, spread 0%. Illustrative rule: `max(floor, min(cap, participation × index_return − spread))`. Explain that this contract-dependent example is separate from the constant-8% IUL model. |

## Essential explanations

- IUL is permanent insurance; a 20-year premium schedule does not guarantee a paid-up policy. Continuing charges can require further funding.
- A 0% index-credit floor does not prevent cash-value losses from charges. Missing premiums stops contributions while charges continue; lapse can follow. Do not invent missed-payment penalties.
- Surrender charges can leave proceeds below premiums paid and surrender ends coverage. ETFs can be sold during market hours, but losses, settlement and taxes affect access.
- Under the level-benefit assumption, beneficiaries receive $214,000 while coverage remains in force, not $214,000 plus cash value. Living-benefit advances generally reduce the remaining death benefit.
- ETF investing alone provides no insurance. Term + ETF includes temporary protection, not permanent coverage. Keep investment balances and insurance payouts separate.
- This compares realized past ETF returns with a reconstructed IUL model calibrated to a reported illustration, not two verified historical product outcomes. Past returns do not establish future results.

## Design and verification

Use concise copy, consistent colors, accessible labels, mobile controls, data-table alternatives and CSV export. Display assumptions and actual valuation dates beside results. Disclosure: “Historical ETF backtest and a reconstructed IUL model. Neither guarantees future outcomes.”

Verify 240 deposits and $72,000 paid in the default 20-year window; the IUL checkpoints above; approximately 6.424675% cash-value-equivalent annual return; approximately $49.26 versus $57.78 in the interest-convention sensitivity; zero-return balances equal net contributions; iterative and direct ETF calculations agree; dividends and splits are handled once; fund inception and missing-data limits are enforced; date windows match; latest-close valuation adds no premature deposit. Require nonnegative budgets and charges, charges within the budget, and valid term premiums. Remove the old assumed **$170,065 VOO value** and **$27,393 gap**: historical results must come from data. Check that all IUL outputs retain their model labels, surrender values are not represented as verified without evidence, and the return card explains its treatment of insurance and exit costs.

## Sources

Fund inception facts checked 2026-09-22. Add the chosen historical-data source and retrieval date when implementing. The user's policy figures remain unverified until the actual illustration is supplied.

- [Vanguard: VOO fact sheet, inception and total-return conventions](https://fund-docs.vanguard.com/F0968.pdf)
- [State Street: SPY inception and fund information](https://www.ssga.com/us/en/institutional/etfs/state-street-spdr-sp-500-etf-trust-spy)
- [NAIC: Life insurance illustrations](https://content.naic.org/insurance-topics/life-insurance-illustrations)
- [New York DFS: Universal life mechanics and charges](https://www.dfs.ny.gov/consumers/life_insurance)
- [FINRA: Surrender charges and policy exchanges](https://www.finra.org/investors/insights/should-you-exchange-your-life-insurance-policy)
