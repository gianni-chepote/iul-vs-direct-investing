// Phase 3 verification harness. Runs before any UI is built.
// Run: node "fins2026/IUL vs Direct Investing/scripts/verify.mjs"
//   or, from the project dir: node scripts/verify.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULTS, prepareWindow, computeScenario, fittedMonthlyCharge,
  iulFlat, iulIndexed, etfBacktest, etfDirect, validateInputs, returnOnPremium,
} from "../app/calc.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const prices = JSON.parse(fs.readFileSync(path.join(HERE, "../data/prices.json"), "utf8"));

let pass = 0, fail = 0;
const near = (a, b, tol = 1e-6) => Math.abs(a - b) <= tol;
function check(name, cond, detail = "") {
  if (cond) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}${detail ? "  <- " + detail : ""}`); }
}
function section(t) { console.log(`\n${t}`); }

// --- default 20-year SPY window ------------------------------------------------
const end = prices.meta.last_completed_month_end;
const spyM = prices.spy.monthly;
const endIdx = spyM.findIndex((r) => r.date === end);
const start = spyM[endIdx - 239].date;
const w = prepareWindow(prices, "SPY", start, end);
const s = computeScenario(w);

section("Default window structure");
check("240 monthly deposits", w.periods === 240, `got ${w.periods}`);
check("$72,000 contributed", near(s.contributed, 72000), `got ${s.contributed}`);
check("window ends at last completed month", w.lastDate === end, w.lastDate);
check("no premature deposit (contributed = budget x periods)",
  near(s.contributed, DEFAULTS.budget * w.periods));

section("IUL-A advertised checkpoints");
check("final = $142,672", near(s.iulA.finalValue, 142672, 0.5), s.iulA.finalValue.toFixed(4));
check("implied charges ~ $11,822", Math.round(s.iulA.impliedCharges) === 11822, s.iulA.impliedCharges.toFixed(2));
check("net contributions ~ $60,178", Math.round(s.iulA.netContributed) === 60178, s.iulA.netContributed.toFixed(2));
check("modeled growth ~ $82,494", Math.round(s.iulA.modeledGrowth) === 82494, s.iulA.modeledGrowth.toFixed(2));
check("fitted charge displays $49.26", near(fittedMonthlyCharge(), 49.257938, 1e-5), fittedMonthlyCharge().toFixed(6));
check("return on full premium ~ 6.4247%", near(s.returnOnPremium, 0.064247, 1e-5), (s.returnOnPremium * 100).toFixed(4));

section("ETF cross-check and drawdown");
check("iterative vs direct agree to the cent", near(s.etf.finalValue, s.etfDirectCheck, 0.01),
  `${s.etf.finalValue.toFixed(6)} vs ${s.etfDirectCheck.toFixed(6)}`);
check("worst drawdown is a real loss in [-100%,0)", s.drawdown.worst < 0 && s.drawdown.worst > -1,
  (s.drawdown.worst * 100).toFixed(1) + "%");

section("IUL-B index-linked mechanics");
check("20 annual credits over 20 years", s.iulB.credits.length === 20, `${s.iulB.credits.length}`);
check("every credit within [floor, cap]",
  s.iulB.credits.every((c) => c.creditRate >= DEFAULTS.floor - 1e-12 && c.creditRate <= DEFAULTS.cap + 1e-12));
check("IUL-B ends below the advertised IUL-A (caps + no dividends bite)",
  s.iulB.finalValue < s.iulA.finalValue, `B ${s.iulB.finalValue.toFixed(0)} vs A ${s.iulA.finalValue.toFixed(0)}`);

// Synthetic all-flat index -> every credit at the floor.
{
  const flat = new Array(w.periods + 1).fill(100);
  const b = iulIndexed(w.periods, DEFAULTS.budget, s.charge, flat, DEFAULTS);
  check("synthetic flat index credits the floor every year",
    b.credits.every((c) => near(c.creditRate, DEFAULTS.floor)));
}
// Synthetic +20%/yr index -> every credit at the cap.
{
  const up = Array.from({ length: w.periods + 1 }, (_, i) => Math.pow(1.2, i / 12));
  const b = iulIndexed(w.periods, DEFAULTS.budget, s.charge, up, DEFAULTS);
  check("synthetic +20%/yr index credits the cap every year",
    b.credits.every((c) => near(c.creditRate, DEFAULTS.cap)));
}
// Dividends are excluded: crediting on price index < crediting on total-return levels.
{
  const trRatios = w.etfLevels; // SPY adj close = total return
  // Build a total-return "index" anchored to the same first value for a fair swap.
  const trIndex = [trRatios[0] * (w.indexLevels[0] / w.indexLevels[1])];
  for (const v of trRatios) trIndex.push(v);
  const bPrice = iulIndexed(w.periods, DEFAULTS.budget, s.charge, w.indexLevels, DEFAULTS);
  const bTotal = iulIndexed(w.periods, DEFAULTS.budget, s.charge, trIndex, DEFAULTS);
  check("IUL-B on price index < IUL-B on total-return index (dividends excluded)",
    bPrice.finalValue < bTotal.finalValue,
    `${bPrice.finalValue.toFixed(0)} vs ${bTotal.finalValue.toFixed(0)}`);
}

section("Zero-return identities");
{
  const flatLevels = new Array(w.periods).fill(200);
  const etf0 = etfBacktest(flatLevels, DEFAULTS.budget);
  check("flat ETF ending value equals total contributed",
    near(etf0.finalValue, DEFAULTS.budget * w.periods));
  const iulA0 = iulFlat(w.periods, DEFAULTS.budget, s.charge, 0);
  check("zero-credit IUL-A equals net contributions",
    near(iulA0.finalValue, (DEFAULTS.budget - s.charge) * w.periods));
  const flatIdx = new Array(w.periods + 1).fill(100);
  const iulB0 = iulIndexed(w.periods, DEFAULTS.budget, s.charge, flatIdx, DEFAULTS);
  check("zero-credit IUL-B equals net contributions",
    near(iulB0.finalValue, (DEFAULTS.budget - s.charge) * w.periods));
}

section("VOO shorter-window recalculation");
{
  const vooM = prices.voo.monthly;
  const vStart = vooM[0].date, vEnd = vooM[vooM.length - 1].date;
  const wv = prepareWindow(prices, "VOO", vStart, vEnd);
  const sv = computeScenario(wv);
  check("VOO window is shorter than 240 months", wv.periods < 240, `${wv.periods}`);
  check("VOO IUL-A recomputed over its own window (not $142,672)",
    !near(sv.iulA.finalValue, 142672, 1), sv.iulA.finalValue.toFixed(0));
  check("VOO contributed = budget x its own periods", near(sv.contributed, DEFAULTS.budget * wv.periods));
  check("no legacy $170,065 VOO value", !near(sv.etf.finalValue, 170065, 1) && !near(sv.iulA.finalValue, 170065, 1));
  check("no legacy $27,393 gap", !near(sv.etf.finalValue - sv.iulA.finalValue, 27393, 1));
}

section("Data-integrity guards throw, not fabricate");
check("VOO before inception yields no months (throws, no backfill)", (() => {
  try { prepareWindow(prices, "VOO", "2000-01-01", "2005-12-31"); return false; } catch { return true; }
})());
check("empty window throws rather than returning zeros", (() => {
  try { prepareWindow(prices, "SPY", "2030-01-01", "2030-12-31"); return false; } catch { return true; }
})());

section("Input guards");
check("valid defaults pass", validateInputs().length === 0);
check("charge above budget rejected", validateInputs({ monthlyCharge: 400 }).length > 0);
check("negative budget rejected", validateInputs({ budget: -1 }).length > 0);
check("cap below floor rejected", validateInputs({ cap: 0.02, floor: 0.05 }).length > 0);
check("term premium >= budget rejected", validateInputs({}, 300).length > 0);
check("negative term premium rejected", validateInputs({}, -5).length > 0);

console.log(`\n${fail === 0 ? "ALL PASS" : "FAILURES PRESENT"}  (${pass} passed, ${fail} failed)`);
process.exit(fail === 0 ? 0 : 1);
