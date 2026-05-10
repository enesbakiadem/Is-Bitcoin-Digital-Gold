"""
q5_drawdown.py
--------------
Q5 — What was the worst loss each asset experienced, and how long did recovery take?

Two angles:

  a) Maximum Drawdown (MDD)
     Largest peak-to-trough decline in the full period.
     MDD = (trough - peak) / peak
     The single most important risk metric for long-term investors.

  b) Drawdown history → CSV for Power BI
     Rolling drawdown over time: at each day, how far are we from
     the previous all-time high?
     Exported for Power BI — visually shows crash periods and recoveries.

Why this matters:
  Q2 showed BTC has the best CAGR. But a 68% drawdown means an investor
  who bought at the peak lost two thirds of their money before recovering.
  MDD puts the Q2 returns in context — high return, extreme risk.
  Gold's MDD tells a very different story.

Usage
------
    python src/q5_drawdown.py
"""

import json
import pandas as pd
import numpy as np
from config import F_PRICES, PROCESSED, TICKERS

# ── Load data ─────────────────────────────────────────────────────────────────
prices = pd.read_csv(F_PRICES, index_col="date", parse_dates=True)
ASSETS = list(TICKERS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# a) Maximum Drawdown
# ─────────────────────────────────────────────────────────────────────────────
def calc_drawdown_series(series: pd.Series) -> pd.Series:
    """
    Rolling drawdown from previous all-time high.
    Returns a series of values in % (negative = below ATH).
    """
    rolling_max = series.cummax()
    drawdown    = (series - rolling_max) / rolling_max * 100
    return drawdown


def max_drawdown(series: pd.Series) -> dict:
    """
    Finds the maximum drawdown, its peak date, trough date,
    and recovery date (first day price returns to previous peak).
    """
    drawdown    = calc_drawdown_series(series)
    mdd         = drawdown.min()
    trough_date = drawdown.idxmin()
    peak_date   = series[:trough_date].idxmax()

    # Recovery: first date after trough where price >= peak price
    peak_price    = series[peak_date]
    after_trough  = series[trough_date:]
    recovered     = after_trough[after_trough >= peak_price]
    recovery_date = recovered.index[0] if not recovered.empty else None

    # Days peak→trough, trough→recovery
    days_to_trough   = (trough_date - peak_date).days
    days_to_recovery = (recovery_date - trough_date).days if recovery_date else None

    return {
        "max_drawdown_pct":   round(mdd, 2),
        "peak_date":          str(peak_date.date()),
        "trough_date":        str(trough_date.date()),
        "recovery_date":      str(recovery_date.date()) if recovery_date else "not yet recovered",
        "days_peak_to_trough":   days_to_trough,
        "days_trough_to_recovery": days_to_recovery if days_to_recovery else "n/a",
    }


# ─────────────────────────────────────────────────────────────────────────────
# b) Rolling drawdown → CSV for Power BI
# ─────────────────────────────────────────────────────────────────────────────
def rolling_drawdown() -> pd.DataFrame:
    """
    Daily drawdown from ATH for each asset.
    Exported as drawdown_history.csv for Power BI.
    """
    dd = pd.DataFrame(index=prices.index)
    for asset in ASSETS:
        dd[f"{asset}_drawdown_pct"] = calc_drawdown_series(prices[asset]).round(2)

    out_path = PROCESSED / "drawdown_history.csv"
    dd.to_csv(out_path)
    print(f"[OK] drawdown_history.csv  ({len(dd)} rows) → {out_path}")
    return dd


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== a) Maximum Drawdown ===")
    results = {}
    for asset in ASSETS:
        results[asset] = max_drawdown(prices[asset])

    # Summary table
    print(f"\n  {'Asset':<6}  {'Max DD':>8}  {'Peak':>12}  {'Trough':>12}  {'Recovery':>12}  {'Days down':>10}  {'Days up':>8}")
    print("  " + "-" * 80)
    for asset, r in sorted(results.items(), key=lambda x: x[1]["max_drawdown_pct"]):
        print(
            f"  {asset:<6}  "
            f"{r['max_drawdown_pct']:>7.2f}%  "
            f"{r['peak_date']:>12}  "
            f"{r['trough_date']:>12}  "
            f"{str(r['recovery_date']):>12}  "
            f"{str(r['days_peak_to_trough']):>10}  "
            f"{str(r['days_trough_to_recovery']):>8}"
        )

    print("\n=== b) Drawdown history → CSV ===")
    rolling_drawdown()

    # Save
    out_path = PROCESSED / "q5_drawdown.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] q5_drawdown.json → {out_path}")