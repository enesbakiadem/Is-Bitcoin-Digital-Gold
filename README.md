# Asset Comparison Analysis — BTC / Gold / World ETF (2015–2026)

Empirical comparison of Bitcoin, Gold (GLD), and a global equity ETF (ACWI) across correlation, real returns, and the "Digital Gold" hypothesis.

All prices in USD. Analysis period: January 2015 – May 2026, constrained by BTC data availability.

---

## Research Questions

**Q1 — Correlation & Crisis Behavior**
How correlated are the three assets overall, and does this change across different market regimes (pre-COVID, COVID crash, bull run 2021, rate hike cycle 2022)?

**Q2 — Real Returns**
Who actually grew purchasing power since 2015, after adjusting for inflation? Nominal CAGR vs. real CAGR, and what $1,000 invested at the start is worth today in real terms.

**Q3 — Is Bitcoin "Digital Gold"?**
Gold has two well-established properties: inflation hedge and safe haven. Does BTC share these empirically? Three sub-tests: inflation correlation, safe haven behavior during equity crashes, and rate sensitivity.

---

## Key Findings

### Q1 — Correlation

| Pair | Full period | Rate hikes 2022 | Bull run 2021 |
|------|------------|-----------------|---------------|
| BTC vs. GOLD | r = 0.06 | r = 0.34 | r = -0.04 |
| BTC vs. ETF | r = 0.32 | r = 0.52 | r = 0.53 |
| GOLD vs. ETF | r = 0.21 | r = 0.39 | r = 0.39 |

BTC has virtually no correlation with Gold over the full period. It correlates more with equities — particularly during stress periods. In 2022, BTC and the World ETF moved together significantly (r=0.52), suggesting BTC behaves as a risk-on asset rather than a defensive one.

### Q2 — Real Returns (inflation-adjusted, base $1,000)

| Asset | Nominal CAGR | Real CAGR | $1,000 → (nominal) | $1,000 → (real) |
|-------|-------------|-----------|-------------------|-----------------|
| BTC | 68.4% | 63.4% | $350,883 | $249,380 |
| Gold | 11.6% | 8.3% | $3,432 | $2,439 |
| ETF | 11.1% | 7.8% | $3,259 | $2,316 |

Inflation eroded ~28.9% of purchasing power over the period. All three assets outpaced inflation significantly. Gold and the World ETF delivered near-identical returns — surprising given their very different risk profiles. BTC is in a different league entirely, though its ~80% drawdown periods (2018, 2022) make the realized return highly dependent on entry and exit timing.

### Q3 — Digital Gold Test

**a) Inflation hedge:** None of the three assets shows a reliable positive correlation with monthly CPI inflation. BTC is mildly negative (r=-0.21, p=0.018). This does not contradict Q2 — all three beat inflation *long-term* — but none reliably rises *when* inflation spikes month-to-month. Gold's inflation hedge reputation is not supported empirically in this dataset.

**b) Safe haven:** In the worst 20% of equity months (ETF ≤ -2.26%):
- BTC averaged **-3.86%** — falls with equities, not a safe haven
- Gold averaged **-0.12%** — holds stable, consistent with safe haven behavior

This is the clearest finding of the project. When markets panic, BTC sells off alongside equities. Gold does not.

**c) Rate sensitivity:** BTC shows limited rate sensitivity overall (r=-0.08) but a stronger negative response during the 2022 rate hike cycle specifically (r=-0.36), coinciding with BTC's collapse from ~$65k to ~$16k. Gold and the ETF show no clear rate sensitivity.

**Structural note:** Bitcoin has a hard supply cap of 21 million coins — architecturally similar to gold's physical scarcity. This is the theoretical foundation of the "Digital Gold" argument. Empirically, however, BTC behaves more like a high-volatility growth asset than a monetary store of value. The supply cap may become more relevant as the asset matures and volatility decreases.

---

## Data Sources

| Source | What | Series |
|--------|------|--------|
| [Yahoo Finance](https://finance.yahoo.com) via `yfinance` | Daily closing prices: BTC-USD, GLD, ACWI | — |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | US CPI (monthly) | CPIAUCSL |
| [FRED](https://fred.stlouisfed.org) via `fredapi` | Fed Funds Rate (monthly) | FEDFUNDS |

---

## Project Structure

```
asset-comparison-analysis/
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
│   ├── config.py              # Paths, tickers, FRED key, date range
│   ├── prepare_data.py        # Download + clean all data → processed/
│   ├── q1_correlation.py      # Correlation analysis across market regimes
│   ├── q2_real_returns.py     # Nominal vs. real CAGR, $1000 scenarios
│   └── q3_digital_gold.py     # Inflation hedge, safe haven, rate sensitivity
├── visual/                    # Power BI dashboard (coming)
└── README.md
```

---

## Reproducing the Analysis

```bash
pip install pandas yfinance fredapi scipy
```

Add your FRED API key to `src/config.py` (free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)), then:

```bash
python src/prepare_data.py
python src/q1_correlation.py
python src/q2_real_returns.py
python src/q3_digital_gold.py
```