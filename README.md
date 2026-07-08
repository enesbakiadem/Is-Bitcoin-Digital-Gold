# Is Bitcoin Digital Gold?

## 📌 Project Snapshot

- **Type:** end-to-end data analysis project
- **Tools:** Python, pandas, SciPy, Power BI
- **Data:** Yahoo Finance, FRED
- **Assets:** Bitcoin, gold, global equities
- **Focus:** correlation, safe-haven behavior, real returns, volatility, drawdowns
- **Output:** Reproducible Python pipeline, Power BI dashboard, static dashboard screenshots

## 🔑 Key Takeaway

Bitcoin shares gold’s scarcity narrative, but not its observed market behavior.

From 2014 to 2026, Bitcoin delivered much higher returns than gold and global equities, but also showed deeper drawdowns, higher volatility, weak correlation with gold, and no clear safe-haven behavior during bad equity months.

> Scarcity is similar. Behavior, so far, is not.

## 🧭 Overview

Bitcoin is often described as “digital gold” because of its fixed supply and independence from traditional monetary systems.

But scarcity alone does not guarantee gold-like behavior.

This project tests whether Bitcoin has behaved like gold in market data by comparing Bitcoin, gold, and global equities across returns, correlations, drawdowns, volatility, and safe-haven behavior.

## 📸 Dashboard Preview

The final Power BI dashboard tells the story across four pages.

### 1. Verdict
![Hero page](./visuals/1_hero.png)

### 2. Return Path
![Return path](./visuals/2_return_path.png)

### 3. Correlation Behavior
![Correlation behavior](./visuals/3_correlation_behavior.png)

### 4. Final Scorecard
![Scorecard](./visuals/4_scorecard.png)

The interactive Power BI file is available as:

```text
btc-digital-gold-dashboard.pbix
```

## 🎯 Research Question

Bitcoin is often called “digital gold” because of its fixed supply.

This project asks:

> Does Bitcoin only resemble gold in its scarcity narrative, or has it also behaved like gold in market data?

To test this, the analysis compares three assets:

| Asset           | Ticker  | Role                             |
| --------------- | ------- | -------------------------------- |
| Bitcoin         | BTC-USD | Digital gold candidate           |
| Gold            | GLD     | Traditional safe-haven benchmark |
| Global equities | ACWI    | Risk-asset benchmark             |

## 🧠 Analytical Framing

Gold is commonly viewed as a store of value and partial safe-haven asset.

For Bitcoin to behave like “digital gold”, scarcity alone is not enough. It should also show at least some gold-like market behavior.

This project therefore separates the narrative from the data and tests five questions:

* Does Bitcoin move like gold?
* Does Bitcoin hold up when global equities fall?
* How do real returns, volatility, and drawdowns compare?
* Is there any clear inflation-hedge signal?
* Overall, does Bitcoin’s market behavior support the digital-gold narrative?

## 📊 Data Sources

| Source                       | Data                        | Series / Tickers   |
| ---------------------------- | --------------------------- | ------------------ |
| Yahoo Finance via `yfinance` | Daily adjusted close prices | BTC-USD, GLD, ACWI |
| FRED via `fredapi`           | US CPI inflation            | CPIAUCSL           |
| FRED via `fredapi`           | Fed Funds Rate              | FEDFUNDS           |

## 📆 Analysis Period

The analysis uses the longest common period available for Bitcoin, gold, and global equities:

```text
2014-09-17 to 2026-04-30
```

Only dates with valid prices for all three assets are included.

No forward-fill is applied across asset calendars. This keeps the comparison consistent and avoids carrying prices across non-overlapping trading days.

## ⚙️ Methodology

The project uses a reproducible Python pipeline:

1. Download daily prices for BTC, gold, and global equities
2. Inner-join assets on common trading days
3. Calculate monthly returns
4. Add macro data from FRED
5. Run digital gold tests:

   * Spearman correlation
   * Safe-haven behavior in bad equity months
   * Inflation sensitivity
   * Rate sensitivity
   * Real returns
   * Volatility
   * Maximum drawdown
6. Export clean CSV files for Power BI

### Why Spearman correlation?

Spearman correlation is used because Bitcoin returns are highly non-normal and fat-tailed.

Unlike Pearson correlation, Spearman does not assume a linear relationship or normally distributed returns. It measures whether two assets tend to move in the same rank order.

### Safe-haven test

Bad equity months are defined as the worst 20% of monthly global equity returns.

The test asks:

> When equities perform poorly, does Bitcoin behave more like gold or more like a risk asset?

## 📈 Key Results

### 1. Bitcoin did not behave like a safe haven

During the worst 20% of monthly global equity returns, gold stayed essentially flat while Bitcoin fell with equities.

| Asset           | Average return during bad equity months |
| --------------- | --------------------------------------: |
| Gold            |                                  +0.02% |
| Bitcoin         |                                  -3.77% |
| Global equities |                                  -5.18% |

This is one of the clearest findings against the digital-gold safe-haven claim.

### 2. Bitcoin did not move like gold

Full-period Spearman correlation of monthly returns:

| Pair                       | Spearman r | Interpretation     |
| -------------------------- | ---------: | ------------------ |
| Bitcoin vs gold            |       0.09 | Near zero          |
| Bitcoin vs global equities |       0.38 | Modest, but higher |
| Gold vs global equities    |       0.25 | Weak/modest        |

Bitcoin was closer to global equities than to gold, but neither relationship was strong.

This does not mean Bitcoin behaved like an equity clone. It means Bitcoin did not behave like gold.

### 3. Bitcoin delivered the highest returns, but with much higher risk

| Asset           | Real CAGR | Max drawdown | Annualized volatility |
| --------------- | --------: | -----------: | --------------------: |
| Bitcoin         |    53.30% |      -83.04% |                66.41% |
| Gold            |     8.62% |      -22.00% |                15.94% |
| Global equities |     7.46% |      -33.53% |                16.93% |

Bitcoin dominated total returns, but its downside risk and volatility were not gold-like.

Gold also performed strongly over the period and quietly outperformed global equities on a real-return basis.

### 4. Inflation-hedge behavior was inconclusive

None of the assets showed clear monthly inflation-hedge behavior.

This does not mean the assets failed to beat inflation over the full period. It means they did not reliably rise in the same months when inflation was high.

## 🧾 Final Interpretation

Bitcoin shares gold’s scarcity narrative, but not its observed market behavior.

The strongest case for Bitcoin as “digital gold” is narrative-based:

* fixed supply
* independent monetary design
* high long-term return potential

The weaker case is behavioral:

* weak correlation with gold
* no clear safe-haven behavior in bad equity months
* much deeper drawdowns than gold
* substantially higher volatility

Final takeaway:

> Scarcity is similar. Behavior, so far, is not.

## ⚠️ Limitations

Bitcoin is a young asset.

This analysis covers most of Bitcoin’s liquid market history, but only a small slice of gold’s much longer monetary history. Bitcoin’s behavior may change as the asset matures, adoption broadens, and market structure evolves.

Additional limitations:

* GLD is used as a tradable gold proxy, not physical gold
* ACWI is used as a global equity proxy
* Correlation does not imply causation
* Safe-haven behavior is tested using the worst 20% of monthly global equity returns, which is intuitive but not universal
* Inflation sensitivity is descriptive and does not prove or disprove long-term inflation-hedge properties

## 🛠️ Tools

* Python
* pandas
* SciPy
* yfinance
* fredapi
* Power BI
* Git / GitHub

## 🔁 Reproducing the Analysis

Install dependencies:

```bash
pip install pandas yfinance fredapi scipy python-dotenv
```

Create a `.env` file with your FRED API key:

```text
FRED_API_KEY=your_key_here
```

Then run:

```bash
py src/prepare_data.py
py src/q1_correlation.py
py src/q2_real_returns.py
py src/q3_digital_gold.py
py src/q4_volatility.py
py src/q5_drawdown.py
py src/export_for_bi.py
```

The Power BI-ready CSV files are written to:

```text
data/processed/bi/
```

## 🤖 Use of AI

AI tools were used to support project structuring, wording, debugging, and code refinement.

The core analysis, interpretation, and final decisions were developed independently.