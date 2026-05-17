"""
q3_digital_gold.py
------------------
Q3 — Is Bitcoin "Digital Gold"?

Gold has two well-established properties:
  1. Inflation hedge  — rises as purchasing power falls
  2. Safe haven       — holds value when equity markets crash

This script tests whether BTC shares these properties empirically.
ETH and EM are included as comparison benchmarks.

Three sub-tests:

  a) Inflation hedge
     Spearman correlation between monthly asset returns and YoY CPI.
     A true hedge rises when inflation rises.

  b) Safe haven
     Average returns during the worst 20% of equity months (ETF).
     A safe haven stays flat or positive when stocks crash.
     Gold is the classical benchmark here.

  c) Rate sensitivity
     Spearman correlation between Fed Funds Rate changes and returns.
     Rising rates = tighter money.
     Theory: growth assets (BTC, ETH, EM) may fall; gold may hold better
     if it behaves as a safe haven.

Usage
------
    python src/q3_digital_gold.py
"""

import json
import pandas as pd
from scipy import stats
from config import F_MASTER, F_RETURNS, PROCESSED, TICKERS

# ── Load data ─────────────────────────────────────────────────────────────────
master  = pd.read_csv(F_MASTER,  index_col="date", parse_dates=True)
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)

macro_m = master[["inflation_yoy", "FED_FUNDS"]].resample("MS").last()
macro_m["FED_FUNDS_change"] = macro_m["FED_FUNDS"].diff()

ASSETS      = list(TICKERS.keys())
RETURN_COLS = {a: f"{a}_return_pct" for a in ASSETS}

ret_m    = returns[[f"{a}_return_pct" for a in ASSETS]]
combined = ret_m.join(macro_m, how="inner").dropna()


# ─────────────────────────────────────────────────────────────────────────────
# a) Inflation hedge
# ─────────────────────────────────────────────────────────────────────────────
def test_inflation_hedge() -> dict:
    """
    Spearman correlation between monthly returns and YoY CPI inflation.

    r > 0.2  and p < 0.05 → inflation hedge
    r < -0.2 and p < 0.05 → loses value when inflation rises
    otherwise             → inconclusive
    """
    results = {}
    for asset in ASSETS:
        r, p = stats.spearmanr(combined[RETURN_COLS[asset]], combined["inflation_yoy"])
        results[asset] = {
            "spearman_r": round(r, 4),
            "p_value":    round(p, 4),
            "verdict": (
                "inflation hedge"         if r >  0.2 and p < 0.05
                else "not an inflation hedge" if r < -0.2 and p < 0.05
                else "inconclusive"
            ),
        }
    return results


# ─────────────────────────────────────────────────────────────────────────────
# b) Safe haven
# ─────────────────────────────────────────────────────────────────────────────
def test_safe_haven() -> dict:
    """
    Splits months into worst 20% and best 20% equity months (ETF returns).
    Checks average return of each asset in both buckets.

    Safe haven: positive or near-zero in bad equity months.
    Gold is the classical safe haven benchmark.
    BTC hypothesis: should be positive if it's "digital gold".
    """
    low_thresh  = combined["ETF_return_pct"].quantile(0.20)
    high_thresh = combined["ETF_return_pct"].quantile(0.80)

    bad_months  = combined[combined["ETF_return_pct"] <= low_thresh]
    good_months = combined[combined["ETF_return_pct"] >= high_thresh]

    results = {
        "equity_bad_threshold_pct":  round(low_thresh,  2),
        "equity_good_threshold_pct": round(high_thresh, 2),
        "n_bad_months":              len(bad_months),
        "n_good_months":             len(good_months),
        "assets": {}
    }

    for asset in ASSETS:
        col      = RETURN_COLS[asset]
        avg_bad  = bad_months[col].mean()
        avg_good = good_months[col].mean()
        r, p     = stats.spearmanr(combined[col], combined["ETF_return_pct"])

        results["assets"][asset] = {
            "avg_return_bad_equity_months":  round(avg_bad,  2),
            "avg_return_good_equity_months": round(avg_good, 2),
            "correlation_with_equity_r":     round(r, 4),
            "verdict": (
                "safe haven"                        if avg_bad > 0    and r < 0.2
                else "not a safe haven"             if avg_bad < -2   and r > 0.3
                else "partial / inconclusive"
            ),
        }
    return results


# ─────────────────────────────────────────────────────────────────────────────
# c) Rate sensitivity
# ─────────────────────────────────────────────────────────────────────────────
def test_rate_sensitivity() -> dict:
    """
    Spearman correlation between Fed Funds Rate changes and asset returns.
    Negative r = falls when rates rise (rate-sensitive).

    Also computed for the 2022 rate hike cycle specifically,
    where the Fed raised rates aggressively from ~0% to 5.25%.
    """
    rate_hike = combined.loc["2022-01-01":"2023-12-01"]

    results = {}
    for asset in ASSETS:
        col    = RETURN_COLS[asset]
        r, p   = stats.spearmanr(combined[col], combined["FED_FUNDS_change"])

        if len(rate_hike) >= 6:
            r_h, p_h = stats.spearmanr(rate_hike[col], rate_hike["FED_FUNDS_change"])
        else:
            r_h, p_h = None, None

        results[asset] = {
            "full_period": {
                "spearman_r": round(r,   4),
                "p_value":    round(p,   4),
            },
            "rate_hike_2022_2023": {
                "spearman_r": round(r_h, 4) if r_h is not None else None,
                "p_value":    round(p_h, 4) if p_h is not None else None,
            },
            "verdict": (
                "rate-sensitive (falls when rates rise)" if r < -0.15 and p < 0.05
                else "rate-insensitive"                  if abs(r) < 0.1
                else "inconclusive"
            ),
        }
    return results


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== a) Inflation Hedge ===")
    a = test_inflation_hedge()
    print(f"  {'Asset':<6}  {'r':>8}  {'p':>8}  verdict")
    print("  " + "-" * 50)
    for asset, res in a.items():
        print(f"  {asset:<6}  {res['spearman_r']:>8}  {res['p_value']:>8}  {res['verdict']}")

    print("\n=== b) Safe Haven ===")
    b = test_safe_haven()
    print(f"  Bad equity months: ETF ≤ {b['equity_bad_threshold_pct']}%  (n={b['n_bad_months']})")
    print(f"\n  {'Asset':<6}  {'Bad months':>12}  {'Good months':>12}  {'r vs ETF':>10}  verdict")
    print("  " + "-" * 70)
    for asset, res in b["assets"].items():
        print(
            f"  {asset:<6}  "
            f"{res['avg_return_bad_equity_months']:>11.2f}%  "
            f"{res['avg_return_good_equity_months']:>11.2f}%  "
            f"{res['correlation_with_equity_r']:>10}  "
            f"{res['verdict']}"
        )

    print("\n=== c) Rate Sensitivity ===")
    c = test_rate_sensitivity()
    print(f"  {'Asset':<6}  {'r (full)':>10}  {'r (2022 hikes)':>15}  verdict")
    print("  " + "-" * 60)
    for asset, res in c.items():
        r_full = res['full_period']['spearman_r']
        r_hike = res['rate_hike_2022_2023']['spearman_r']
        print(f"  {asset:<6}  {r_full:>10}  {str(r_hike):>15}  {res['verdict']}")

    # Save
    out = {"a_inflation_hedge": a, "b_safe_haven": b, "c_rate_sensitivity": c}
    out_path = PROCESSED / "q3_digital_gold.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n[OK] Saved → {out_path}")