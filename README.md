# Asset Comparison Analysis — BTC / ETH / Gold / World ETF / EM / Bonds (2017–2026)

Empirical comparison of six assets across correlation, real returns, volatility, drawdown, Sharpe ratio, seasonality, and the "Digital Gold" hypothesis. All prices in USD. Analysis period: November 2017 – April 2026, constrained by ETH data availability.

**Status: Work in progress.** SQL analysis complete. Power BI dashboard coming next.

---

## Assets

| Key | Ticker | Description |
|-----|--------|-------------|
| BTC | BTC-USD | Bitcoin |
| ETH | ETH-USD | Ethereum |
| GOLD | GLD | SPDR Gold Shares ETF |
| ETF | ACWI | iShares MSCI All Country World ETF |
| EM | EEM | iShares MSCI Emerging Markets ETF |
| BOND | TLT | iShares 20+ Year Treasury Bond ETF (US Treasuries) |

**Note on BOND:** TLT reflects mark-to-market prices of long-duration US Treasuries. An investor who buys an actual government bond and holds it to maturity receives 100% of face value back plus coupon payments — no nominal loss. The negative returns shown here reflect what a TLT ETF holder would have experienced if selling during the 2022 rate hike cycle. German investors typically prefer Bunds (EU government bonds); the EZB raised rates more slowly than the Fed, so a Bund-based equivalent would show a smaller 2022 drawdown — but the same directional relationship between rates and bond prices applies.

---

## Research Questions

**Q1 — Correlation & Crisis Behavior**
How correlated are the assets across different market regimes?

**Q2 — Real Returns**
Who actually grew purchasing power since 2017, after adjusting for US CPI inflation?

**Q3 — Is Bitcoin "Digital Gold"?**
Three sub-tests: inflation hedge, safe haven behavior, rate sensitivity.

**Q4 — Volatility**
Which asset is most volatile, and is BTC becoming calmer over time?

**Q5 — Maximum Drawdown**
Worst peak-to-trough loss and recovery time for each asset.

**Q6 — Sharpe Ratio**
Best return per unit of risk — who was most efficient?

**Q7 — Seasonality**
Are there systematic monthly patterns? Does "Sell in May" hold?

**SQL — Cross-table queries**
Ad-hoc analysis using SQLite: yearly winners, simultaneous crashes, safe haven scorecard.

---

## Key Findings

### Q1 — Correlation (Spearman, monthly returns)

| Pair | Full period | Bull 2021 | Rate hikes 2022 | Post-hikes 2024+ |
|------|------------|-----------|-----------------|-----------------|
| BTC vs. GOLD | 0.09 ✗ | -0.10 | 0.35 | -0.16 |
| BTC vs. ETF | 0.38 ✓ | 0.51 | 0.50 | 0.49 |
| BTC vs. ETH | 0.78 ✓ | 0.70 | 0.91 | 0.78 |
| BTC vs. BOND | 0.05 ✗ | -0.06 | 0.27 | -0.15 |
| GOLD vs. BOND | 0.36 ✓ | 0.28 | 0.50 | 0.28 |

✓ = statistically significant (p < 0.05), ✗ = not significant

BTC has virtually no correlation with Gold (r=0.09, not significant) and correlates significantly more with equities (r=0.38). BTC and ETH move almost in lockstep (r=0.78, rising to r=0.91 during 2022 rate hikes) — crypto diversification between BTC and ETH is largely an illusion.

### Q2 — Real Returns (inflation-adjusted, base $1,000 invested Nov 2017)

| Asset | Nominal CAGR | Real CAGR | $1,000 → nominal | $1,000 → real |
|-------|-------------|-----------|-----------------|---------------|
| BTC | 26.97% | 22.68% | $7,456 | $5,582 |
| ETH | 21.21% | 17.12% | $5,046 | $3,778 |
| GOLD | 16.05% | 12.13% | $3,498 | $2,619 |
| ETF | 11.38% | 7.61% | $2,476 | $1,854 |
| EM | 6.45% | 2.85% | $1,692 | $1,267 |
| BOND | -1.68% | -5.01% | $867 | $649 |
| Cash | 0% | — | $1,000 | $720 |

Inflation eroded ~28% of purchasing power over the period. Gold outperformed the World ETF — notable given its lower equity correlation. The universal takeaway: invest in something.

### Q3 — Digital Gold Test

**a) Inflation hedge:** No asset shows reliable positive correlation with monthly CPI. None qualifies as an inflation hedge on a month-to-month basis — including Gold. This does not contradict Q2: all assets beat inflation long-term, but none reliably rises *when* inflation spikes.

**b) Safe haven — worst 20% of equity months (ETF ≤ -2.91%):**

| Asset | Avg return in bad equity months | Verdict |
|-------|--------------------------------|---------|
| BTC | -4.65% | not a safe haven |
| ETH | -6.67% | not a safe haven |
| GOLD | -0.65% | partial safe haven |
| BOND | -2.00% | partial — inconsistent |
| EM | -5.08% | not a safe haven |

**c) Rate sensitivity:** Gold is the most rate-sensitive asset (r=-0.224, significant) — it competes with yield-bearing alternatives. BTC shows rate sensitivity only during the active 2022 hike cycle (r=-0.389), not as a structural property.

**Overall verdict: BTC is not Digital Gold.** It fails all three tests. BTC is a high-volatility risk-on asset that moves with equities, sells off in crashes, and shows no inflation hedge properties. Gold remains the only asset with consistent (if imperfect) safe haven behavior. Bitcoin's hard supply cap of 21 million coins — the theoretical foundation of the "Digital Gold" argument — does not yet translate into the same behavioral properties. BTC's declining volatility (see Q4) suggests this may change as the asset matures.

### Q4 — Volatility (annualized)

| Asset | Ann. Volatility |
|-------|----------------|
| ETH | 86.3% |
| BTC | 66.1% |
| EM | 21.1% |
| ETF | 18.1% |
| GOLD | 16.5% |
| BOND | 15.5% |

BTC's volatility has declined significantly over time: 135% in 2017 → 40% in 2025. Gold has remained stable at ~13-20%. The gap is closing — but BTC remains 3-4x more volatile than Gold.

### Q5 — Maximum Drawdown

| Asset | Max Drawdown | Peak | Trough | Recovery | Days down | Days up |
|-------|-------------|------|--------|----------|-----------|---------|
| ETH | -93.5% | Jan 2018 | Dec 2018 | Jan 2021 | 339 | 767 |
| BTC | -83.0% | Dec 2017 | Dec 2018 | Nov 2020 | 361 | 717 |
| BOND | -48.4% | Aug 2020 | Oct 2023 | not recovered | 1171 | — |
| EM | -39.8% | Feb 2021 | Oct 2022 | Sep 2025 | 614 | 1057 |
| ETF | -33.5% | Feb 2020 | Mar 2020 | Aug 2020 | 40 | 154 |
| GOLD | -22.0% | Aug 2020 | Sep 2022 | Mar 2024 | 781 | 525 |

ETF had the fastest recovery by far (154 days). BTC and ETH had the deepest drawdowns but eventually recovered. BOND has not recovered — its 2020 peak remains out of reach. Note: BOND's drawdown reflects TLT ETF mark-to-market pricing; a buy-and-hold investor in actual Treasury bonds would face no nominal loss at maturity.

### Q6 — Sharpe Ratio (risk-adjusted return, risk-free rate: 2.58% p.a.)

| Asset | Sharpe | Bull 2021 | Rate hikes 2022 | Post-hikes 2024+ |
|-------|--------|-----------|-----------------|-----------------|
| GOLD | 0.90 | 0.03 | 0.28 | 1.96 |
| BTC | 0.64 | 1.41 | 0.17 | 0.68 |
| ETH | 0.62 | 1.89 | 0.02 | 0.29 |
| ETF | 0.60 | 1.49 | -0.05 | 1.49 |
| EM | 0.29 | 1.16 | -0.37 | 1.38 |
| BOND | -0.23 | -0.76 | -0.96 | -0.37 |

Gold has the best risk-adjusted return overall (Sharpe 0.90) — not BTC. BTC has higher absolute returns but also much higher volatility. For a risk-aware investor, Gold is the more efficient asset. BOND is the only asset with a negative Sharpe — holding cash would have been superior.

### Q7 — Seasonality (notable patterns, n≈8 per month)

**BTC:** Best month October (+14.4% avg, 75% hit rate — "Uptober" confirmed). Worst month August (-5.2%, only 25% hit rate). July also strong (+10.3%, 75%).

**Gold:** December strongest (88.9% hit rate — positive in almost every year). September consistently weak (25% hit rate).

**ETF:** July was positive in 100% of years in the dataset. November strong (87.5% hit rate, +4.3% avg).

**"Sell in May":** Not supported. May was positive for all assets, ETF at 75% hit rate.

*Note: with ~8 observations per month, these patterns are indicative rather than statistically robust.*

### SQL — Notable Findings

**Yearly winners (best asset each year):**

| Year | Winner | Est. Annual Return |
|------|--------|-------------------|
| 2017 | ETH | +823% |
| 2018 | BOND | -1.2% (least bad) |
| 2019 | BTC | +97% |
| 2020 | ETH | +236% |
| 2021 | ETH | +217% |
| 2022 | GOLD | +0.04% (least bad) |
| 2023 | BTC | +108% |
| 2024 | BTC | +98% |
| 2025 | GOLD | +51% |
| 2026 | EM | +52% (YTD) |

In 2018 and 2022, the "winner" simply lost the least. No asset dominated every year — the strongest argument for diversification in the dataset.

**BTC >10% while Gold negative:** Occurred 15 times. In Risk-On rallies, capital rotates aggressively from Gold into BTC — they compete for the same "alternative asset" allocation. This is the opposite of correlated behavior.

**Simultaneous crash months (BTC, ETH, ETF all < -5%):** Only 3 months in the full period. Gold was near-neutral in all three; BOND was a safe haven only in March 2020 (COVID), but crashed alongside everything else in April 2022 when rates rose.

**Safe haven scorecard (33 months where ETF was negative):**
- Gold average return: **+0.06%** — holds flat
- BOND average return: **-1.17%** — loses value

Gold protects. BOND (TLT) does not — at least not in a rate-hike dominated period.

---

## Data Sources

| Source | What | Tickers / Series |
|--------|------|-----------------|
| [Yahoo Finance](https://finance.yahoo.com) via `yfinance` | Daily adjusted close prices | BTC-USD, ETH-USD, GLD, ACWI, EEM, TLT |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | US CPI (monthly) | CPIAUCSL |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | Fed Funds Rate (monthly) | FEDFUNDS |

**Methodology note:** Only real trading days are used (inner join across all assets). No forward-fill across weekends — avoids artificial correlation between assets with different trading schedules. FRED API key loaded from `.env`, never hardcoded.

---

## Project Structure

```
asset-comparison-analysis/
├── .env.example               # Copy to .env, add FRED API key
├── queries.sql                # SQL queries for DB Browser for SQLite
├── data/
│   ├── raw/                   # Not tracked by git
│   └── processed/
│       ├── prices_daily.csv
│       ├── macro_monthly.csv
│       ├── returns.csv
│       ├── master.csv
│       ├── rolling_volatility.csv
│       ├── drawdown_history.csv
│       ├── rolling_sharpe.csv
│       ├── seasonality.csv
│       ├── assets.db          # SQLite database
│       └── *.json             # Per-question result summaries
├── src/
│   ├── config.py              # Paths, tickers, date range, FRED key via .env
│   ├── prepare_data.py        # Download + clean all data
│   ├── load_to_sqlite.py      # Load processed CSVs into assets.db
│   ├── q1_correlation.py
│   ├── q2_real_returns.py
│   ├── q3_digital_gold.py
│   ├── q4_volatility.py
│   ├── q5_drawdown.py
│   ├── q6_sharpe.py
│   └── q7_seasonality.py
├── visual/                    # Power BI dashboard (coming)
└── README.md
```

---

## Reproducing the Analysis

```bash
pip install pandas yfinance fredapi scipy python-dotenv
```

Copy `.env.example` to `.env` and add your FRED API key (free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)), then:

```bash
python src/prepare_data.py
python src/q1_correlation.py
python src/q2_real_returns.py
python src/q3_digital_gold.py
python src/q4_volatility.py
python src/q5_drawdown.py
python src/q6_sharpe.py
python src/q7_seasonality.py
python src/load_to_sqlite.py
# Open data/processed/assets.db in DB Browser for SQLite
# Run queries from queries.sql
```