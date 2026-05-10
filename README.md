# Asset Comparison Analysis — BTC / ETH / Gold / World ETF / EM / Bonds (2017–2026)

Empirical comparison of six assets across correlation, real returns, and the "Digital Gold" hypothesis. All prices in USD. Analysis period: November 2017 – April 2026, constrained by ETH data availability.

**Status: Work in progress.** Q1–Q3 complete. Q4 (Volatility), Q5 (Drawdown), Q6 (Sharpe Ratio), Q7 (Seasonality), and Power BI dashboard coming next.

---

## Assets

| Key | Ticker | Description |
|-----|--------|-------------|
| BTC | BTC-USD | Bitcoin |
| ETH | ETH-USD | Ethereum |
| GOLD | GLD | SPDR Gold Shares ETF |
| ETF | ACWI | iShares MSCI All Country World ETF |
| EM | EEM | iShares MSCI Emerging Markets ETF |
| BOND | TLT | iShares 20+ Year Treasury Bond ETF |

---

## Research Questions

**Q1 — Correlation & Crisis Behavior**
How correlated are the assets across different market regimes? Does BTC move with Gold or with equities?

**Q2 — Real Returns**
Who actually grew purchasing power since 2017, after adjusting for US CPI inflation? Nominal vs. real CAGR, and what $1,000 invested at the start is worth today.

**Q3 — Is Bitcoin "Digital Gold"?**
Gold has two well-established properties: inflation hedge and safe haven. Does BTC share these empirically? Three sub-tests: inflation correlation, safe haven behavior during equity crashes, and rate sensitivity.

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

BTC has virtually no correlation with Gold over the full period (r=0.09, not significant). It correlates significantly with equities (r=0.38) and very strongly with ETH (r=0.78). During the 2022 rate hike cycle, BTC and ETH moved almost in lockstep (r=0.91). Gold and Bonds show moderate positive correlation (r=0.36) — both behaving as defensive assets. BTC behaves as a risk-on asset, not a defensive one.

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

Inflation eroded ~28% of purchasing power over the period. All assets except Bonds outpaced inflation. Gold outperformed the World ETF — notable given its lower correlation with equities. Bonds were the worst performer: the 2022 rate hike cycle crushed long-duration treasury prices. BTC and ETH lead by a wide margin but with extreme volatility and timing dependency — the CAGR assumes holding through -80% drawdowns.

### Q3 — Digital Gold Test

**a) Inflation Hedge**

No asset shows a reliable positive correlation with monthly CPI inflation. All results are inconclusive or mildly negative. EM is the only statistically significant result — and it's negative (r=-0.28, p=0.004), meaning EM tends to fall when inflation rises. The popular narrative that Gold or BTC protect against inflation is not supported empirically in this dataset. Note: this tests month-to-month co-movement with inflation, not long-term purchasing power preservation (see Q2 for that).

**b) Safe Haven — behavior during worst 20% of equity months (ETF ≤ -2.91%)**

| Asset | Avg return in bad equity months | Verdict |
|-------|--------------------------------|---------|
| BTC | -4.65% | not a safe haven |
| ETH | -6.67% | not a safe haven |
| GOLD | -0.65% | partial safe haven |
| BOND | -2.00% | partial safe haven |
| EM | -5.08% | not a safe haven |

Gold is the only asset that holds near-flat when equities crash. Bonds underperformed their theoretical safe-haven role — hurt by the 2022 environment where rates rose and equities fell simultaneously. BTC and ETH fall harder than equities in bad months, confirming risk-on behavior.

**c) Rate Sensitivity**

| Asset | r (full period) | r (2022 hike cycle) | Verdict |
|-------|----------------|---------------------|---------|
| BTC | -0.151 | -0.389 | inconclusive |
| ETH | -0.038 | -0.229 | rate-insensitive |
| GOLD | -0.224 | -0.253 | rate-sensitive ✓ |
| ETF | -0.077 | +0.013 | rate-insensitive |
| EM | -0.128 | -0.034 | inconclusive |
| BOND | -0.106 | -0.021 | inconclusive |

Counterintuitively, Gold is the most rate-sensitive asset (r=-0.224, significant). Gold pays no yield, so rising rates make it relatively less attractive vs. interest-bearing alternatives. BTC shows rate sensitivity only during the active 2022 hike cycle — not as a structural property.

**Overall verdict: BTC is not Digital Gold.**
It fails all three tests. BTC is empirically a high-volatility risk-on asset that moves with equities and ETH, sells off in crashes, and shows no reliable inflation hedge properties. Gold remains the only asset with genuine (if imperfect) safe haven characteristics. The theoretical argument for BTC — a hard supply cap of 21 million coins, analogous to gold's physical scarcity — does not yet translate into the same behavioral properties. This may change as the asset matures.

---

## Data Sources

| Source | What | Tickers / Series |
|--------|------|-----------------|
| [Yahoo Finance](https://finance.yahoo.com) via `yfinance` | Daily adjusted close prices | BTC-USD, ETH-USD, GLD, ACWI, EEM, TLT |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | US CPI (monthly) | CPIAUCSL |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | Fed Funds Rate (monthly) | FEDFUNDS |

**Note on methodology:** Only real trading days are used (inner join across all assets). No forward-fill across weekends or holidays — this avoids artificial correlation inflation between assets with different trading schedules (crypto trades 7 days/week, traditional assets 5 days).

---

## Project Structure

```
asset-comparison-analysis/
├── .env.example           # Copy to .env and add your FRED API key
├── data/
│   ├── raw/               # Not tracked by git
│   └── processed/         # Generated outputs
│       ├── prices_daily.csv
│       ├── macro_monthly.csv
│       ├── returns.csv
│       ├── master.csv
│       ├── q1_correlation.json
│       ├── q2_real_returns.json
│       └── q3_digital_gold.json
├── src/
│   ├── config.py              # Paths, tickers, date range, FRED key via .env
│   ├── prepare_data.py        # Download + clean all data → processed/
│   ├── q1_correlation.py      # Correlation across market regimes
│   ├── q2_real_returns.py     # Nominal vs. real CAGR, $1,000 scenarios
│   └── q3_digital_gold.py     # Inflation hedge, safe haven, rate sensitivity
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
```