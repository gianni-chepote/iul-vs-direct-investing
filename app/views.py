"""Client-facing comparison, protection and methodology views."""

from __future__ import annotations

from html import escape

import charts
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from model import (
    ETF_LABEL,
    IUL_LABEL,
    PAID_LABEL,
    TERM_LABEL,
    apply_surrender,
    compare,
    drawdown,
    premium_return,
    validate_illustration,
)

from fintools.apps import render_csv_download, render_display_table


def money(value):
    return f"${value:,.0f}"


def pct(value):
    return "Not available" if value is None else f"{value:.2%}"


def cards(items):
    markup = '<div class="cards">'
    for i, (label, value, foot) in enumerate(items):
        cls = "card featured" if i == 1 else "card"
        markup += (
            f'<div class="{cls}"><div class="label">{escape(label)}</div>'
            f'<div class="value">{escape(value)}</div>'
            f'<div class="foot">{escape(foot)}</div></div>'
        )
    st.markdown(markup + "</div>", unsafe_allow_html=True)


def chart(fig, key):
    st.plotly_chart(
        fig,
        width="stretch",
        theme=None,
        key=key,
        config={"displaylogo": False, "scrollZoom": False},
    )


def rate_explanation(result, budget, credit):
    rate = premium_return(budget, len(result), result[IUL_LABEL].iloc[-1])
    st.markdown(
        f'<div class="rate-note"><strong>{credit:.1%} assumed credited rate</strong>'
        f" &nbsp;→&nbsp; <strong>{pct(rate)} cash-value-equivalent annual return</strong><br>"
        "The credited rate grows the cash value. The second rate compares the ending account "
        "value with every dollar of your premiums, including the portion used for charges. "
        "It excludes insurance protection, surrender charges and personal taxes.</div>",
        unsafe_allow_html=True,
    )


def render_compare(*, ticker, budget, charge, credit, monthly, daily, result, meta, latest_window):
    final = result.iloc[-1]
    count = len(result)
    gap = final[ETF_LABEL] - final[IUL_LABEL]
    cards(
        [
            ("Total contributed", money(final[PAID_LABEL]), f"{count} payments × {money(budget)}"),
            (
                f"{ticker} · historical",
                money(final[ETF_LABEL]),
                "Dividends reinvested · fund costs embedded",
            ),
            (
                "Reconstructed IUL model",
                money(final[IUL_LABEL]),
                "Illustrative account value · before surrender",
            ),
            ("ETF minus modeled IUL", money(gap), "Different returns, costs and protection"),
        ]
    )
    first, last = result.index[0], result.index[-1]
    st.markdown(
        f'<div class="story">Had you invested <strong>{money(budget)} each month in {ticker}</strong>'
        f" from {first:%b %d, %Y} to {last:%b %d, %Y}, your {money(final[PAID_LABEL])} "
        f"would have been worth approximately <strong>{money(final[ETF_LABEL])}</strong> "
        f"as of {last:%b %d, %Y}, with dividends reinvested. "
        f"Historical gain/loss: <strong>{money(final[ETF_LABEL] - final[PAID_LABEL])}</strong>. "
        "Before personal taxes and trading costs.</div>",
        unsafe_allow_html=True,
    )
    st.subheader("The same budget. Different paths.")
    chart(charts.growth(result, ticker), "growth")
    st.caption(
        "Solid line: historical ETF backtest. Dashed line: reconstructed IUL model. "
        "Only the reported 20-year IUL endpoint was used for calibration; intermediate "
        "balances are not verified policy values. Contributions are made at month-end."
    )
    dd = drawdown(daily, first, last)
    st.subheader("What the journey asked of you")
    st.caption(
        f"Largest historical ETF drawdown in this window: {dd.min():.1f}% "
        f"on {dd.idxmin():%b %d, %Y}. Deposits are excluded from this risk measure."
    )
    chart(charts.drawdowns(dd), "drawdown")
    st.caption(
        "A smooth IUL model does not establish zero policy risk. Charges can reduce cash "
        "value even when the index credit is 0%."
    )
    rate_explanation(result, budget, credit)
    if latest_window and daily.index[-1] > last:
        if st.checkbox("Also show value at the latest available close", key="latest"):
            latest = daily.index[-1]
            growth_factor = daily["Adjusted close"].iloc[-1] / monthly["Adjusted close"].iloc[-1]
            days = max(0, (latest - last.to_period("M").end_time.normalize()).days)
            left, right = st.columns(2)
            left.metric(
                f"{ticker} · historical · {latest:%b %d, %Y}",
                money(final[ETF_LABEL] * growth_factor),
            )
            right.metric(
                f"Reconstructed IUL model · {latest:%b %d, %Y}",
                money(final[IUL_LABEL] * (1 + credit) ** (days / 365.25)),
            )
            st.caption(
                "No contribution for the unfinished month. IUL growth is prorated using "
                "elapsed calendar days / 365.25; no additional month-end charge is assumed. "
                f"Market data retrieved {meta['retrieved_utc']}."
            )
    with st.expander("View the monthly balances"):
        render_display_table(result, height=340)


def render_costs(*, ticker, budget, charge, credit, monthly, daily, result, meta, latest_window):
    st.subheader("Understand what the premium buys")
    st.caption("IUL combines insurance and cash value. An ETF provides investment exposure only.")
    chart(charts.allocation(budget, charge), "allocation")
    st.caption(
        "Implied by the model; not verified policy fees. Actual charges may change with "
        "age and policy terms. The entire ending-value gap is not a fee estimate."
    )
    count = len(result)
    ending = result.iloc[-1]
    breakdown = pd.DataFrame(
        {
            "Component": [
                "Total premiums paid",
                "Implied charges — not verified",
                "Net cash-value contributions",
                "Modeled growth",
                "Reconstructed IUL account value",
            ],
            "Amount (USD)": [
                budget * count,
                charge * count,
                (budget - charge) * count,
                ending[IUL_LABEL] - (budget - charge) * count,
                ending[IUL_LABEL],
            ],
        }
    )
    render_display_table(breakdown, reset_index=False, height=215)
    rate_explanation(result, budget, credit)

    st.subheader("Protection is a separate benefit")
    st.info(
        "The example reports a $214,000 death benefit. Under a level-benefit assumption, "
        "beneficiaries receive that amount while coverage is in force—not $214,000 plus "
        "cash value. Changing the budget here does not establish that this coverage is funded."
    )
    if st.toggle("Compare term insurance + investing the difference", key="term_enabled"):
        a, b, c = st.columns(3)
        with a:
            term = st.number_input(
                "Monthly term premium (USD)",
                min_value=0.0,
                max_value=budget,
                value=None,
                step=5.0,
                key="term_premium",
                placeholder="Enter a quote",
            )
        with b:
            coverage = st.number_input(
                "Term coverage (USD)",
                min_value=1.0,
                value=None,
                step=10000.0,
                key="term_coverage",
                placeholder="Enter coverage",
            )
        with c:
            years = st.number_input(
                "Term duration (years)", min_value=1, max_value=50, value=20, key="term_years"
            )
        if term is None or coverage is None:
            st.info(
                "Enter a premium and coverage amount to calculate this optional comparison. "
                "An assumed quote is hypothetical; it is not the IUL charge."
            )
        else:
            combined = compare(monthly, budget, charge, credit, term, int(years * 12))
            chart(charts.growth(combined, ticker), "term_growth")
            active = len(combined) <= years * 12
            st.metric("Term + ETF ending investment value", money(combined[TERM_LABEL].iloc[-1]))
            st.caption(
                f"Term coverage: {money(coverage)} for {years} years. "
                f"At the selected endpoint: {'within the insured term' if active else 'term expired'}. "
                "After expiry, the full budget goes into the ETF; no renewed coverage is assumed. "
                "Term insurance is temporary; an IUL is intended as permanent insurance."
            )
            render_csv_download(
                combined,
                label="Download term comparison · CSV",
                file_name="term_etf_comparison.csv",
                key="term_csv",
            )

    st.subheader("What could you actually withdraw?")
    st.caption(
        "The ETF balance is its modeled liquidation value before taxes and trading costs. "
        "An IUL account balance can exceed the amount available on surrender."
    )
    with st.expander("Supply a surrender schedule or insurer illustration"):
        st.markdown(
            "**Surrender-charge schedule:** provide `Date` and `Surrender charge (USD)` "
            "columns, using dates from the comparison CSV. Only supplied dates are used."
        )
        st.download_button(
            "Download empty surrender schedule template",
            "Date,Surrender charge (USD)\n",
            file_name="surrender_schedule.csv",
        )
        schedule = st.file_uploader("Surrender-charge schedule (CSV)", type="csv", key="schedule")
        if schedule is not None:
            try:
                joined = apply_surrender(result, pd.read_csv(schedule))
                fig = charts.growth(result, ticker)
                col = "Modeled surrender value; not insurer-verified (USD)"
                fig.add_trace(
                    go.Scatter(
                        x=joined.index,
                        y=joined[col],
                        mode="markers",
                        name="Modeled surrender · not insurer-verified",
                        marker=dict(color="#7f5b78", size=7),
                    )
                )
                chart(fig, "surrender")
                st.caption(
                    "A supplied charge schedule does not verify the reconstructed account "
                    "balance. These points are modeled, not insurer-verified surrender values."
                )
                render_display_table(joined[[IUL_LABEL, "Surrender charge (USD)", col]], height=260)
            except (ValueError, KeyError, TypeError, pd.errors.ParserError) as exc:
                st.error(str(exc))
        else:
            st.info("Policy surrender information required. No zero-fee assumption is made.")
        st.markdown(
            "**Insurer-provided annual illustration:** upload dated account and surrender "
            "values with guarantee status. Imported points remain projections, not history."
        )
        st.download_button(
            "Download empty illustration template",
            "Date,Account value (USD),Cash surrender value (USD),Guarantee status\n",
            file_name="insurer_illustration.csv",
        )
        uploaded = st.file_uploader("Insurer illustration (CSV)", type="csv", key="illustration")
        if uploaded is not None:
            try:
                illustration = validate_illustration(pd.read_csv(uploaded))
                fig = charts.growth(result, ticker)
                for status, group in illustration.groupby("Guarantee status"):
                    for col in ["Account value (USD)", "Cash surrender value (USD)"]:
                        fig.add_trace(
                            go.Scatter(
                                x=group.Date,
                                y=group[col],
                                mode="markers",
                                name=f"Supplied {status.lower()} {col.lower()}",
                                marker=dict(size=8),
                            )
                        )
                chart(fig, "insurer_values")
                st.caption(
                    "User-supplied insurer-provided illustrated values, not independently "
                    "authenticated. No values are interpolated between the supplied dates."
                )
                render_display_table(illustration, reset_index=False, height=260)
            except (ValueError, KeyError, TypeError, pd.errors.ParserError) as exc:
                st.error(str(exc))
    st.markdown(
        "**Early exit:** surrender charges can leave you with less than your premiums "
        "paid, and surrender ends coverage. ETF sales involve market risk and settlement. "
        "A 20-year payment plan does not guarantee that an IUL is fully paid up; policy "
        "charges may continue for life."
    )


def render_method(*, ticker, budget, charge, credit, monthly, daily, result, meta, latest_window):
    st.subheader("Two kinds of evidence. Clearly separated.")
    st.markdown(
        "**ETF:** actual historical adjusted-price returns with dividends reinvested. "
        "**IUL:** a reconstructed constant-charge model calibrated to a user-reported "
        "$142,672 value at year 20. The policy's actual fees, annual values and rate "
        "convention have not been verified."
    )
    with st.expander("Why 8% credited interest is not an 8% return on premiums", expanded=True):
        rate_explanation(result, budget, credit)
        st.latex(r"FV = P\frac{(1+r)^n-1}{r},\qquad R_{annual}=(1+r)^{12}-1")
        st.markdown(
            "For the advertised example, solve for the monthly rate using the full "
            "$300 premium, 240 month-end payments and $142,672 of account value. "
            "That yields approximately **6.42% effective annually**. It excludes the "
            "value of insurance, taxes and any surrender charge."
        )
        st.markdown(
            "**Rate convention matters:** 8% effective annually implies about $49.26 "
            "in equivalent monthly charges. An 8% nominal rate compounded monthly "
            "would imply about $57.78 for the same target. Neither is a verified fee quote."
        )
    with st.expander("How the index-credit formula works"):
        a, b, c = st.columns(3)
        cap = a.slider("Illustrative cap (%)", 0.0, 20.0, 8.0, 0.5)
        participation = b.slider("Illustrative participation (%)", 0.0, 200.0, 80.0, 5.0)
        spread = c.slider("Illustrative spread (percentage points)", 0.0, 10.0, 0.0, 0.5)
        chart(charts.mechanics(cap, participation, spread), "mechanics")
        st.latex(r"credit=\max(0,\min(cap,\ participation\times index\ return-spread))")
        st.caption(
            "A contract-dependent teaching example. These controls do not change the "
            "constant-rate reconstruction. The index price return excludes dividends; "
            "the ETF historical return includes reinvested dividends."
        )
    with st.expander("Calculation details and important limitations"):
        st.latex(r"IUL_t=IUL_{t-1}(1+m)+P-C,\quad m=(1+R)^{1/12}-1")
        st.latex(r"ETF_T=\sum_k P_k\frac{A_T}{A_k}")
        st.markdown(
            "Contributions occur at month-end; fractional investing is assumed. "
            "A is a dividend- and split-adjusted price. Its ratios incorporate distributions "
            "and embedded fund expenses: no second fee or dividend adjustment is applied. "
            "Personal taxes, commissions, spreads, withdrawals and loans are excluded."
        )
        st.markdown(
            "**Missing premiums:** cash contributions stop but ongoing policy charges "
            "continue. Cash value can fall and coverage can lapse. No automatic penalty "
            "or participation-rate change is assumed; missed payments are not simulated here."
        )
        st.markdown(
            "**Living benefits:** qualifying riders may advance part of a death benefit "
            "and reduce the remaining amount. An increasing-benefit option differs from "
            "the assumed level benefit. **Unknown early values:** fitting one ending "
            "value cannot establish the insurer's intervening cash or surrender values."
        )
        st.markdown(
            "SPY supplies the full 20-year ETF history. VOO has history only from "
            "September 2010. Neither historical results nor a smooth insurance model "
            "predict future returns. The insurer's reason for using 8% is unknown."
        )
    with st.expander("Data provenance, observations and downloads", expanded=True):
        st.markdown(
            f"**Provider:** {meta['provider']} · **Fund:** {ticker} · "
            f"**Status:** {meta['status']}\n\n"
            f"**Coverage:** {meta['first_observation']} to {meta['last_observation']} · "
            f"**Daily observations:** {meta['rows']:,}\n\n"
            f"**Retrieved (UTC):** {meta['retrieved_utc']}\n\n"
            f"**Selected contributions:** {len(result)} · "
            f"{result.index[0]:%Y-%m-%d} to {result.index[-1]:%Y-%m-%d}\n\n"
            f"**Adjustments:** {meta['adjustment']}"
        )
        selected = daily.loc[result.index[0] : result.index[-1]]
        render_display_table(selected, height=300)
        render_csv_download(
            selected,
            label="Download selected daily prices · CSV",
            file_name=f"{ticker}_daily_adjusted.csv",
            key="daily_csv",
        )
    st.markdown(
        "**Sources**\n\n"
        "- [Vanguard: VOO inception and return conventions](https://fund-docs.vanguard.com/F0968.pdf)\n"
        "- [State Street: SPY](https://www.ssga.com/us/en/institutional/etfs/state-street-spdr-sp-500-etf-trust-spy)\n"
        f"- [Yahoo Finance: historical {ticker} data](https://finance.yahoo.com/quote/{ticker}/history/)\n"
        "- [NAIC: life insurance illustrations](https://content.naic.org/insurance-topics/life-insurance-illustrations)\n"
        "- [New York DFS: universal life mechanics](https://www.dfs.ny.gov/consumers/life_insurance)\n"
        "- [FINRA: surrender charges](https://www.finra.org/investors/insights/should-you-exchange-your-life-insurance-policy)"
    )
