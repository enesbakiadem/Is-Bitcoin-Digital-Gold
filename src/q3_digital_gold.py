"""
q3_digital_gold.py
------------------
Q3 — Is Bitcoin actually "Digital Gold"?

Gold has two well-established properties:
  1. Inflation hedge  — rises as purchasing power falls
  2. Safe haven       — holds value when equity markets crash

This script tests whether BTC shares these properties empirically.
Three sub-tests:

  a) Inflation hedge: does the asset return correlate with CPI inflation?
  b) Safe haven: what happens to BTC and Gold when equities have their
     worst months? A true safe haven should stay flat or rise.
  c) Rate sensitivity: how do assets respond to Fed rate changes?
     Rising rates = tighter money = typically bad for growth assets.
     Gold is theoretically mixed; BTC should behave like a growth asset.

Usage
------
    python src/q3_digital_gold.py
"""

import json
import pandas as pd
from scipy import stats
from config import F_MASTER, F_RETURNS, PROCESSED

# ── Load data ─────────────────────────────────────────────────────────────────
master  = pd.read_csv(F_MASTER,  index_col="date", parse_dates=True)
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)

# Monthly macro
macro_m = master[["inflation_yoy", "FED_FUNDS"]].resample("MS").last()
macro_m["FED_FUNDS_change"] = macro_m["FED_FUNDS"].diff()

# Monthly returns
ret_m = returns[["BTC_return_pct", "GOLD_return_pct", "ETF_return_pct"]]

# Merge — only rows where all data exists
combined = ret_m.join(macro_m, how="inner").dropna()

ASSETS = {
    "BTC":  "BTC_return_pct",
    "GOLD": "GOLD_return_pct",
    "ETF":  "ETF_return_pct",
}


# ─────────────────────────────────────────────────────────────────────────────
# a) Inflation hedge
# ─────────────────────────────────────────────────────────────────────────────
def test_inflation_hedge() -> dict:
    """
    Spearman correlation between monthly asset returns and YoY CPI inflation.

    A true inflation hedge should show positive correlation:
    when inflation rises, the asset price rises too.

    r > 0.2 and significant → inflation hedge
    r ~ 0                   → no relationship
    r < -0.2                → loses value when inflation rises (bad hedge)
    """
    results = {}
    for asset, col in ASSETS.items():
        r, p = stats.spearmanr(combined[col], combined["inflation_yoy"])
        results[asset] = {
            "spearman_r": round(r, 4),
            "p_value":    round(p, 4),
            "n_months":   len(combined),
            "verdict": (
                "inflation hedge" if r > 0.2 and p < 0.05
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
    Splits months into "bad equity months" (worst 20% ETF returns)
    and "good equity months" (best 20%), then checks average BTC
    and Gold returns in each bucket.

    Safe haven logic:
      - In bad equity months: safe haven should be flat or positive
      - In good equity months: safe haven typically lags (that's fine)

    Also computes Spearman correlation between ETF returns and BTC/Gold returns
    to see if BTC falls with equities (= not a safe haven).
    """
    # Worst and best 20% equity months
    low_threshold  = combined["ETF_return_pct"].quantile(0.20)
    high_threshold = combined["ETF_return_pct"].quantile(0.80)

    bad_months  = combined[combined["ETF_return_pct"] <= low_threshold]
    good_months = combined[combined["ETF_return_pct"] >= high_threshold]

    results = {
        "equity_bad_threshold_pct":  round(low_threshold, 2),
        "equity_good_threshold_pct": round(high_threshold, 2),
        "n_bad_months":              len(bad_months),
        "n_good_months":             len(good_months),
        "assets": {}
    }

    for asset, col in {"BTC": "BTC_return_pct", "GOLD": "GOLD_return_pct"}.items():
        avg_bad  = bad_months[col].mean()
        avg_good = good_months[col].mean()

        # Correlation with equity returns
        r, p = stats.spearmanr(combined[col], combined["ETF_return_pct"])

        results["assets"][asset] = {
            "avg_return_in_bad_equity_months":  round(avg_bad, 2),
            "avg_return_in_good_equity_months": round(avg_good, 2),
            "correlation_with_equity_r":        round(r, 4),
            "correlation_p_value":              round(p, 4),
            "verdict": (
                "safe haven" if avg_bad > 0 and r < 0.2
                else "not a safe haven — falls with equities" if avg_bad < -2 and r > 0.3
                else "partial / inconclusive"
            ),
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# c) Rate sensitivity
# ─────────────────────────────────────────────────────────────────────────────
def test_rate_sensitivity() -> dict:
    """
    Spearman correlation between monthly Fed Funds Rate changes
    and asset returns.

    Theory:
      - Rising rates → higher discount rate → growth assets fall (BTC, ETF)
      - Gold: mixed — sometimes seen as rate-sensitive, sometimes not
      - A negative r means "falls when rates rise"

    We also split into rate-hike period (2022–2023) vs. overall
    to see if the relationship was stronger during active tightening.
    """
    rate_hike = combined.loc["2022-01-01":"2023-12-01"]

    results = {}
    for asset, col in ASSETS.items():
        # Full period
        r_full, p_full = stats.spearmanr(combined[col], combined["FED_FUNDS_change"])

        # Rate hike period only
        if len(rate_hike) >= 6:
            r_hike, p_hike = stats.spearmanr(rate_hike[col], rate_hike["FED_FUNDS_change"])
        else:
            r_hike, p_hike = None, None

        results[asset] = {
            "full_period": {
                "spearman_r": round(r_full, 4),
                "p_value":    round(p_full, 4),
            },
            "rate_hike_2022_2023": {
                "spearman_r": round(r_hike, 4) if r_hike else None,
                "p_value":    round(p_hike, 4) if p_hike else None,
            },
            "verdict": (
                "rate-sensitive (falls when rates rise)" if r_full < -0.15 and p_full < 0.05
                else "rate-insensitive" if abs(r_full) < 0.1
                else "inconclusive"
            ),
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== a) Inflation Hedge ===")
    a = test_inflation_hedge()
    for asset, res in a.items():
        print(f"  {asset}: r={res['spearman_r']}  p={res['p_value']}  → {res['verdict']}")

    print("\n=== b) Safe Haven ===")
    b = test_safe_haven()
    print(f"  Bad equity months (ETF ≤ {b['equity_bad_threshold_pct']}%): n={b['n_bad_months']}")
    for asset, res in b["assets"].items():
        print(f"  {asset}:")
        print(f"    avg return in bad months : {res['avg_return_in_bad_equity_months']}%")
        print(f"    avg return in good months: {res['avg_return_in_good_equity_months']}%")
        print(f"    correlation with equity  : r={res['correlation_with_equity_r']}")
        print(f"    verdict                  : {res['verdict']}")

    print("\n=== c) Rate Sensitivity ===")
    c = test_rate_sensitivity()
    for asset, res in c.items():
        r_full = res['full_period']['spearman_r']
        r_hike = res['rate_hike_2022_2023']['spearman_r']
        print(f"  {asset}: r_full={r_full}  r_hike_period={r_hike}  → {res['verdict']}")

    # Save
    out = {"a_inflation_hedge": a, "b_safe_haven": b, "c_rate_sensitivity": c}
    out_path = PROCESSED / "q3_digital_gold.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n[OK] Saved → {out_path}")