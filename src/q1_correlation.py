"""
q1_correlation.py
-----------------
Q1 — How correlated are BTC, Gold, and the World ETF?
And does this change during market stress?

Method: Spearman correlation on monthly returns, computed for
the full period and for specific market regimes.

Spearman is used over Pearson because return distributions —
especially BTC — are fat-tailed, making rank-based correlation
more robust than assuming normality.

Interpretation:
  r > 0.7  → strong positive (move together)
  r ~ 0    → no relationship
  r < -0.3 → tend to move opposite (diversification benefit)

Usage
------
    python src/q1_correlation.py
"""

import json
import pandas as pd
from scipy import stats
from config import F_RETURNS, PROCESSED

# ── Load monthly returns ──────────────────────────────────────────────────────
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)

RETURN_COLS = {
    "BTC":  "BTC_return_pct",
    "GOLD": "GOLD_return_pct",
    "ETF":  "ETF_return_pct",
}

# ── Market regimes to compare ─────────────────────────────────────────────────
PERIODS = {
    "full":        ("2015-01-01", "2026-05-01"),
    "pre_covid":   ("2015-01-01", "2020-02-01"),
    "covid_crash": ("2020-02-01", "2020-06-01"),
    "bull_2021":   ("2020-06-01", "2022-01-01"),
    "rate_hikes":  ("2022-01-01", "2023-12-01"),
    "post_hikes":  ("2024-01-01", "2026-05-01"),
}

PAIRS = [("BTC", "GOLD"), ("BTC", "ETF"), ("GOLD", "ETF")]


# ─────────────────────────────────────────────────────────────────────────────
def correlate_period(start: str, end: str) -> dict:
    """
    Computes Spearman correlation for all three asset pairs
    within a given date range.
    """
    subset = returns.loc[start:end, list(RETURN_COLS.values())].dropna()
    subset.columns = list(RETURN_COLS.keys())

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

    # Print
    for period, data in results.items():
        print(f"\n[{period}]")
        for k, v in data.items():
            if isinstance(v, dict):
                r = v['spearman_r']
                p = v['p_value']
                print(f"  {k}: r={r}  p={p}")
            else:
                print(f"  {k}: {v}")

    # Save
    out_path = PROCESSED / "q1_correlation.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Saved → {out_path}")