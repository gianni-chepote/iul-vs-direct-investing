// Phase 2 calculation engine for the IUL vs. direct-investing webpage.
//
// Pure functions, no DOM. Runs unchanged in the browser (ES module) and in Node
// (for the Phase 3 verification harness), so there is one source of truth.
//
// Series modeled:
//   - ETF backtest        : actual total returns, dividends reinvested.
//   - IUL-A (advertised)  : flat effective-annual credit, monthly recursion.
//   - IUL-B (index-linked): annual point-to-point on the S&P 500 PRICE index,
//                           cap / floor / participation / spread; no dividends.
//
// Honesty invariants encoded here:
//   * ETF uses total-return levels; IUL-B uses price-only index levels.
//   * The IUL monthly charge is fitted once to the advertised ending value and
//     then held fixed; it is never recalibrated per scenario.
//   * Both IUL series share the same premium and charge, so they differ only in
//     how the cash value is credited.

export const DEFAULTS = Object.freeze({
  budget: 300,          // monthly premium / ETF budget, USD
  periods: 240,         // months in the full comparison window (20 years)
  iulAnnualCredit: 0.08,// IUL-A effective annual credited rate (hypothetical)
  target: 142672,       // user-reported 20-year illustrated account value
  cap: 0.08,            // IUL-B annual credit cap
  floor: 0.0,           // IUL-B annual credit floor
  participation: 1.0,   // IUL-B participation rate
  spread: 0.0,          // IUL-B spread (subtracted before cap/floor)
  deathBenefit: 214000, // level coverage (assumed)
});

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

export function clamp(x, lo, hi) {
  return Math.max(lo, Math.min(hi, x));
}

// Effective-annual rate -> equivalent monthly rate.
export function monthlyRateFromAnnual(annual) {
  return Math.pow(1 + annual, 1 / 12) - 1;
}

// Ordinary-annuity future-value factor: sum_{k=0}^{n-1} (1+r)^k.
export function annuityFactor(r, n) {
  if (r === 0) return n;
  return (Math.pow(1 + r, n) - 1) / r;
}

// Fit the constant monthly charge so the flat-credit recursion reaches `target`
// after `periods` months at the given premium. Fitted once; then held fixed.
export function fittedMonthlyCharge({ budget, periods, iulAnnualCredit, target } = DEFAULTS) {
  const m = monthlyRateFromAnnual(iulAnnualCredit);
  const net = target / annuityFactor(m, periods); // required net contribution
  return budget - net;                            // charge = premium - net
}

// ---------------------------------------------------------------------------
// Input guards
// ---------------------------------------------------------------------------

// Returns a list of human-readable problems; empty list means the inputs are
// valid. The UI blocks calculation while any problem remains.
export function validateInputs(config = {}, termPremium = 0) {
  const cfg = { ...DEFAULTS, ...config };
  const errors = [];
  if (!(cfg.budget >= 0)) errors.push("Monthly budget must be zero or positive.");
  const charge = config.monthlyCharge ?? fittedMonthlyCharge(cfg);
  if (!(charge >= 0)) errors.push("Monthly charge must be zero or positive.");
  if (charge > cfg.budget) errors.push("Monthly charge cannot exceed the budget.");
  if (!(cfg.cap >= cfg.floor)) errors.push("Cap must be greater than or equal to the floor.");
  if (!(cfg.participation >= 0)) errors.push("Participation rate must be zero or positive.");
  if (termPremium < 0) errors.push("Term premium must be zero or positive.");
  if (termPremium >= cfg.budget && termPremium > 0)
    errors.push("Term premium must leave a positive amount to invest.");
  return errors;
}

// ---------------------------------------------------------------------------
// ETF backtest (total return)
// ---------------------------------------------------------------------------

// `levels` are month-end total-return levels at each contribution date.
// Iterative recursion: grow the prior balance, then add this month's budget.
export function etfBacktest(levels, budget) {
  const n = levels.length;
  const series = new Array(n);
  let bal = 0;
  for (let t = 0; t < n; t++) {
    if (t > 0) bal *= levels[t] / levels[t - 1];
    bal += budget;
    series[t] = bal;
  }
  return {
    series,
    finalValue: series[n - 1],
    contributed: budget * n,
  };
}

// Independent cross-check: each contribution grows by A[T]/A[k].
export function etfDirect(levels, budget) {
  const T = levels.length - 1;
  let total = 0;
  for (let k = 0; k <= T; k++) total += budget * (levels[T] / levels[k]);
  return total;
}

// ---------------------------------------------------------------------------
// IUL-A: advertised flat-credit line
// ---------------------------------------------------------------------------

export function iulFlat(periods, budget, monthlyCharge, iulAnnualCredit) {
  const m = monthlyRateFromAnnual(iulAnnualCredit);
  const net = budget - monthlyCharge;
  const series = new Array(periods);
  let bal = 0;
  for (let t = 0; t < periods; t++) {
    bal = bal * (1 + m) + net; // grow, then add net contribution at month-end
    series[t] = bal;
  }
  const contributed = budget * periods;
  const netContributed = net * periods;
  return {
    series,
    finalValue: series[periods - 1],
    contributed,
    impliedCharges: monthlyCharge * periods,
    netContributed,
    modeledGrowth: series[periods - 1] - netContributed,
  };
}

// ---------------------------------------------------------------------------
// IUL-B: index-linked line (annual point-to-point, price index only)
// ---------------------------------------------------------------------------

// `indexLevels` has length periods+1: index[0] is the anchor month-end just
// BEFORE the first contribution; index[1..periods] are the contribution months.
// Convention: add the net contribution at each month-end, then on every 12th
// month apply the annual credit to the full balance.
export function iulIndexed(periods, budget, monthlyCharge, indexLevels, params) {
  const { cap, floor, participation, spread } = { ...DEFAULTS, ...params };
  const net = budget - monthlyCharge;
  const series = new Array(periods);
  const credits = []; // {month, indexReturn, creditRate}
  let bal = 0;
  for (let t = 1; t <= periods; t++) {
    bal += net;
    if (t % 12 === 0) {
      const indexReturn = indexLevels[t] / indexLevels[t - 12] - 1;
      const creditRate = clamp(participation * indexReturn - spread, floor, cap);
      bal *= 1 + creditRate;
      credits.push({ month: t, indexReturn, creditRate });
    }
    series[t - 1] = bal;
  }
  const netContributed = net * periods;
  return {
    series,
    finalValue: series[periods - 1],
    contributed: budget * periods,
    impliedCharges: monthlyCharge * periods,
    netContributed,
    modeledGrowth: series[periods - 1] - netContributed,
    credits,
  };
}

// ---------------------------------------------------------------------------
// Drawdown (contribution-free daily return series)
// ---------------------------------------------------------------------------

export function drawdown(dailyLevels) {
  const n = dailyLevels.length;
  const series = new Array(n);
  let runningMax = -Infinity;
  let worst = 0;
  for (let i = 0; i < n; i++) {
    if (dailyLevels[i] > runningMax) runningMax = dailyLevels[i];
    const dd = dailyLevels[i] / runningMax - 1;
    series[i] = dd;
    if (dd < worst) worst = dd;
  }
  return { series, worst };
}

// ---------------------------------------------------------------------------
// Cash-value-equivalent annual return on the FULL premium
// ---------------------------------------------------------------------------

// Solve budget * annuityFactor(r, periods) = endingValue for monthly r, then
// annualize. Returns null when no finite rate exists.
export function returnOnPremium(endingValue, budget, periods) {
  if (endingValue <= 0 || budget <= 0 || periods <= 0) return null;
  const f = (r) => budget * annuityFactor(r, periods) - endingValue;
  // Ending value below total paid implies a negative monthly rate.
  let lo = -0.9 / 1, hi = 1.0; // monthly-rate search bracket
  let flo = f(lo), fhi = f(hi);
  if (flo * fhi > 0) return null; // no sign change in bracket
  for (let i = 0; i < 200; i++) {
    const mid = (lo + hi) / 2;
    const fmid = f(mid);
    if (Math.abs(fmid) < 1e-9) { lo = hi = mid; break; }
    if (flo * fmid < 0) { hi = mid; fhi = fmid; } else { lo = mid; flo = fmid; }
  }
  const monthly = (lo + hi) / 2;
  return Math.pow(1 + monthly, 12) - 1;
}

// ---------------------------------------------------------------------------
// Window preparation from the snapshot payload
// ---------------------------------------------------------------------------

// Slice prices.json for one ETF and a [startIso, endIso] month-end window, and
// build the aligned arrays the engine needs. Throws on misalignment so bad data
// can never pass silently.
export function prepareWindow(prices, ticker, startIso, endIso) {
  const key = ticker.toLowerCase();
  const etfMonthly = prices[key].monthly.filter((r) => r.date >= startIso && r.date <= endIso);
  if (etfMonthly.length === 0) throw new Error(`No ${ticker} month-ends in window`);

  const firstDate = etfMonthly[0].date;
  const lastDate = etfMonthly[etfMonthly.length - 1].date;

  // Index (price) levels keyed by date, plus the anchor month strictly before
  // the first contribution.
  const gspc = prices.gspc.monthly;
  const gspcByDate = new Map(gspc.map((r) => [r.date, r.close]));
  const before = gspc.filter((r) => r.date < firstDate);
  if (before.length === 0) throw new Error("No index anchor month before window start");
  const anchor = before[before.length - 1].close;

  const indexLevels = [anchor];
  const etfLevels = [];
  for (const r of etfMonthly) {
    if (!gspcByDate.has(r.date)) throw new Error(`Index level missing for ${r.date}`);
    etfLevels.push(r.adj_close);
    indexLevels.push(gspcByDate.get(r.date));
  }

  const etfDaily = prices[key].daily
    .filter((r) => r.date >= firstDate && r.date <= lastDate)
    .map((r) => r.adj_close);

  return {
    ticker,
    firstDate,
    lastDate,
    dates: etfMonthly.map((r) => r.date),
    periods: etfMonthly.length,
    etfLevels,
    indexLevels, // length periods + 1 (index 0 is the anchor)
    etfDaily,
  };
}

// ---------------------------------------------------------------------------
// Orchestrator
// ---------------------------------------------------------------------------

// Full scenario for a valid window and input set. `config` overrides DEFAULTS.
// `window` is the object returned by prepareWindow. Optional `termPremium`
// invests the remaining budget in the ETF.
export function computeScenario(window, config = {}, termPremium = 0) {
  const cfg = { ...DEFAULTS, ...config, periods: window.periods };
  const charge = config.monthlyCharge ?? fittedMonthlyCharge({
    budget: cfg.budget,
    periods: DEFAULTS.periods,      // charge is fitted on the 240-month target...
    iulAnnualCredit: cfg.iulAnnualCredit,
    target: cfg.target,
  });

  const etf = etfBacktest(window.etfLevels, cfg.budget);
  const etfCheck = etfDirect(window.etfLevels, cfg.budget);
  const iulA = iulFlat(window.periods, cfg.budget, charge, cfg.iulAnnualCredit);
  const iulB = iulIndexed(window.periods, cfg.budget, charge, window.indexLevels, cfg);
  const dd = drawdown(window.etfDaily);
  const roiPremium = returnOnPremium(iulA.finalValue, cfg.budget, window.periods);

  let termEtf = null;
  if (termPremium > 0 && termPremium < cfg.budget) {
    termEtf = etfBacktest(window.etfLevels, cfg.budget - termPremium);
  }

  return {
    window,
    charge,                       // ...but always applied over the actual window
    contributed: cfg.budget * window.periods,
    etf,
    etfDirectCheck: etfCheck,
    iulA,
    iulB,
    drawdown: dd,
    returnOnPremium: roiPremium,
    termEtf,
    config: cfg,
  };
}
