"""
q7_seasonality.py
-----------------
Q7 — Are there systematic monthly patterns in asset returns?

"Sell in May and go away" is one of the most famous market sayings.
Does it hold? And are there other calendar patterns?

Two angles:

  a) Average return by calendar month
     For each asset: what is the average monthly return in January,
     February, ... December across all years in the dataset?
     Reveals seasonal patterns — e.g. BTC's famous "Uptober".

  b) Hit rate by month
     In what % of years was a given month positive?
     Adds confidence to the averages — a high average driven by one
     outlier year is less reliable than a consistent pattern.

Note on sample size:
  We have ~8 years of data (2017-2026). Each month appears ~8 times.
  Patterns should be treated as indicative, not statistically robust.
  We flag months where the hit rate is ≥ 70% or ≤ 30% as notable.

Usage
------
    python src/q7_seasonality.py
"""

import json
import pandas as pd
import numpy as np
from config import F_RETURNS, PROCESSED, TICKERS

# ── Load monthly returns ──────────────────────────────────────────────────────
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)

ASSETS      = list(TICKERS.keys())
RETURN_COLS = {a: f"{a}_return_pct" for a in ASSETS}
MONTHS      = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}


# ─────────────────────────────────────────────────────────────────────────────
# a) Average return by calendar month
# ─────────────────────────────────────────────────────────────────────────────
def monthly_seasonality() -> dict:
    """
    Mean and median return per calendar month for each asset.
    Also computes hit rate: % of years where that month was positive.
    """
    results = {}
    for asset in ASSETS:
        col = RETURN_COLS[asset]
        ret = returns[col].dropna().copy()
        ret.index = pd.to_datetime(ret.index)

        monthly_stats = {}
        for m in range(1, 13):
            month_data = ret[ret.index.month == m]
            if len(month_data) < 2:
                continue
            monthly_stats[MONTHS[m]] = {
                "avg_return_pct":    round(month_data.mean(), 2),
                "median_return_pct": round(month_data.median(), 2),
                "hit_rate_pct":      round((month_data > 0).mean() * 100, 1),
                "n_observations":    len(month_data),
                "notable": bool((month_data > 0).mean() >= 0.7 or
                (month_data > 0).mean() <= 0.3),
            }

        # Best and worst months
        sorted_months = sorted(monthly_stats.items(), key=lambda x: -x[1]["avg_return_pct"])
        results[asset] = {
            "by_month":    monthly_stats,
            "best_month":  sorted_months[0][0],
            "worst_month": sorted_months[-1][0],
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Export for Power BI
# ─────────────────────────────────────────────────────────────────────────────
def export_seasonality_csv(results: dict) -> None:
    """
    Flat CSV with avg return per month per asset — easy to visualize in Power BI.
    """
    rows = []
    for asset, data in results.items():
        for month, stats in data["by_month"].items():
            rows.append({
                "asset":           asset,
                "month":           month,
                "month_num":       list(MONTHS.values()).index(month) + 1,
                "avg_return_pct":  stats["avg_return_pct"],
                "hit_rate_pct":    stats["hit_rate_pct"],
                "notable":         stats["notable"],
            })

    df = pd.DataFrame(rows).sort_values(["asset", "month_num"])
    out_path = PROCESSED / "seasonality.csv"
    df.to_csv(out_path, index=False)
    print(f"[OK] seasonality.csv  ({len(df)} rows) → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    results = seasonality = monthly_seasonality()

    # Print table per asset — avg return and hit rate
    for asset in ASSETS:
        data = results[asset]
        print(f"\n  {asset}  (best: {data['best_month']}, worst: {data['worst_month']})")
        print(f"  {'Month':<5}  {'Avg':>7}  {'Hit rate':>9}  {'n':>3}")
        print("  " + "-" * 30)
        for month, stats in data["by_month"].items():
            flag = " ◄" if stats["notable"] else ""
            print(
                f"  {month:<5}  "
                f"{stats['avg_return_pct']:>6.2f}%  "
                f"{stats['hit_rate_pct']:>8.1f}%  "
                f"{stats['n_observations']:>3}"
                f"{flag}"
            )

    # "Sell in May" check
    print("\n=== 'Sell in May' check ===")
    print(f"  {'Asset':<6}  {'May avg':>9}  {'May hit rate':>13}")
    print("  " + "-" * 32)
    for asset in ASSETS:
        may = results[asset]["by_month"].get("May", {})
        print(f"  {asset:<6}  {may.get('avg_return_pct', '—'):>8}%  {may.get('hit_rate_pct', '—'):>12}%")

    export_seasonality_csv(results)

    # Save
    out_path = PROCESSED / "q7_seasonality.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] q7_seasonality.json → {out_path}")