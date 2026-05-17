"""
q1_correlation.py
-----------------
Q1 — How correlated are the assets across different market regimes?

Core question: does BTC behave like Gold (low equity correlation, safe haven)
or like a risk-on asset (high equity correlation, sells off in crashes)?

Adding ETH and EM gives context:
- ETH: is BTC unique among crypto or do all cryptos move together?
- EM: does BTC correlate with emerging markets (both seen as "risk-on")?

Method: Spearman correlation on monthly returns per market regime.
Spearman is used over Pearson: BTC/ETH return distributions are
fat-tailed, violating the normality assumption Pearson requires.

Interpretation:
  r > 0.6  → strong positive (move together)
  r ~ 0    → no relationship
  r < -0.3 → tend to move opposite (diversification benefit)

Usage
------
    python src/q1_correlation.py
"""

import json
import pandas as pd
from scipy import stats
from config import F_RETURNS, PROCESSED, TICKERS

# ── Load monthly returns ──────────────────────────────────────────────────────
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)

ASSETS = list(TICKERS.keys())  # BTC, ETH, GOLD, ETF, EM
RETURN_COLS = {a: f"{a}_return_pct" for a in ASSETS}

# ── Market regimes ────────────────────────────────────────────────────────────
# Note: data starts 2017-11-09 due to ETH inner join cutoff
PERIODS = {
    "full":        ("2017-11-01", "2026-05-01"),
    "crypto_bull": ("2017-11-01", "2018-02-01"),   # BTC peak ~$20k
    "covid_crash": ("2020-02-01", "2020-06-01"),
    "bull_2021":   ("2020-06-01", "2022-01-01"),
    "rate_hikes":  ("2022-01-01", "2023-12-01"),
    "post_hikes":  ("2024-01-01", "2026-05-01"),
}

# Pairs of interest — focused on the Digital Gold question
PAIRS = [
    ("BTC",  "GOLD"),   # core question
    ("BTC",  "ETF"),    # BTC vs equities
    ("BTC",  "ETH"),    # crypto internal
    ("BTC",  "EM"),     # BTC vs risk-on EM
    ("GOLD", "ETF"),    # gold vs equities
    ("ETH",  "ETF"),    # ETH vs equities
]


# ─────────────────────────────────────────────────────────────────────────────
def correlate_period(start: str, end: str) -> dict:
    cols = [RETURN_COLS[a] for a in ASSETS]
    subset = returns.loc[start:end, cols].dropna()
    subset.columns = ASSETS

    if len(subset) < 6:
        return {"note": "insufficient data", "n_months": len(subset)}

    result = {"n_months": len(subset)}
    for a, b in PAIRS:
        r, p = stats.spearmanr(subset[a], subset[b])
        result[f"{a}_vs_{b}"] = {
            "spearman_r": round(r, 4),
            "p_value":    round(p, 4),
        }
    return result


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    results = {}
    for period, (start, end) in PERIODS.items():
        results[period] = correlate_period(start, end)

    # Print — focused view
    print(f"\n{'Period':<15} {'BTC/GOLD':>10} {'BTC/ETF':>10} {'BTC/ETH':>10} {'BTC/EM':>10} {'GOLD/ETF':>10}")
    print("-" * 65)
    for period, data in results.items():
        if "note" in data:
            print(f"{period:<15}  insufficient data (n={data['n_months']})")
            continue
        def r(pair): return data.get(pair, {}).get("spearman_r", "—")
        print(
            f"{period:<15}"
            f"{str(r('BTC_vs_GOLD')):>10}"
            f"{str(r('BTC_vs_ETF')):>10}"
            f"{str(r('BTC_vs_ETH')):>10}"
            f"{str(r('BTC_vs_EM')):>10}"
            f"{str(r('GOLD_vs_ETF')):>10}"
        )

    # Full detail
    print("\n--- Full period detail ---")
    full = results["full"]
    for pair, vals in full.items():
        if pair == "n_months":
            continue
        if isinstance(vals, dict):
            sig = "✓" if vals["p_value"] < 0.05 else "✗"
            print(f"  {pair:<20} r={vals['spearman_r']:>7}  p={vals['p_value']}  {sig}")

    # Save
    out_path = PROCESSED / "q1_correlation.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Saved → {out_path}")