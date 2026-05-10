"""
q4_volatility.py
----------------
Q4 — Which asset is most volatile, and has volatility changed over time?

Two angles:

  a) Overall volatility
     Annualized standard deviation of daily returns for each asset.
     Annualized = daily_std * sqrt(252)  [252 trading days/year]
     This is the standard finance metric for risk.

  b) Rolling volatility over time
     30-day rolling window of annualized volatility.
     Exported to CSV for Power BI — shows visually how volatility
     evolves: is BTC becoming "calmer" as it matures?
     Are there volatility spikes during crises?

Why this matters for the Digital Gold question:
  Gold has historically low and stable volatility — a key property
  for a store of value. If BTC is maturing into digital gold,
  its volatility should be converging toward Gold's level over time.

Usage
------
    python src/q4_volatility.py
"""

import json
import pandas as pd
import numpy as np
from config import F_PRICES, F_MASTER, PROCESSED, TICKERS

# ── Load daily prices ─────────────────────────────────────────────────────────
prices = pd.read_csv(F_PRICES, index_col="date", parse_dates=True)
ASSETS = list(TICKERS.keys())

# Daily returns (%)
daily_returns = prices[ASSETS].pct_change() * 100
TRADING_DAYS  = 252


# ─────────────────────────────────────────────────────────────────────────────
# a) Overall annualized volatility
# ─────────────────────────────────────────────────────────────────────────────
def overall_volatility() -> dict:
    """
    Annualized standard deviation of daily returns.
    Also computes per-year breakdown to show trend over time.
    """
    results = {}
    for asset in ASSETS:
        ret = daily_returns[asset].dropna()

        ann_vol = ret.std() * np.sqrt(TRADING_DAYS)

        # Per-year volatility
        yearly = (
            ret.groupby(ret.index.year)
            .std()
            .apply(lambda x: round(x * np.sqrt(TRADING_DAYS), 2))
            .to_dict()
        )

        results[asset] = {
            "annualized_vol_pct":  round(ann_vol, 2),
            "daily_std_pct":       round(ret.std(), 4),
            "by_year":             yearly,
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# b) Rolling 30-day volatility → CSV for Power BI
# ─────────────────────────────────────────────────────────────────────────────
def rolling_volatility() -> pd.DataFrame:
    """
    30-day rolling annualized volatility for each asset.
    Exported as rolling_volatility.csv for Power BI timeline chart.
    """
    rolling = pd.DataFrame(index=prices.index)

    for asset in ASSETS:
        ret = daily_returns[asset]
        rolling[f"{asset}_vol_30d"] = (
            ret.rolling(30).std() * np.sqrt(TRADING_DAYS)
        ).round(2)

    out_path = PROCESSED / "rolling_volatility.csv"
    rolling.to_csv(out_path)
    print(f"[OK] rolling_volatility.csv  ({len(rolling)} rows) → {out_path}")
    return rolling


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== a) Overall Annualized Volatility ===")
    vol = overall_volatility()

    # Summary table
    print(f"\n  {'Asset':<6}  {'Ann. Vol':>10}  {'Daily Std':>10}")
    print("  " + "-" * 32)
    for asset, v in sorted(vol.items(), key=lambda x: -x[1]["annualized_vol_pct"]):
        print(f"  {asset:<6}  {v['annualized_vol_pct']:>9.2f}%  {v['daily_std_pct']:>9.4f}%")

    # Year-by-year for BTC and GOLD
    print(f"\n  Year-by-year — BTC vs GOLD:")
    print(f"  {'Year':<6}  {'BTC':>8}  {'GOLD':>8}")
    print("  " + "-" * 26)
    btc_years  = vol["BTC"]["by_year"]
    gold_years = vol["GOLD"]["by_year"]
    for year in sorted(btc_years.keys()):
        btc_v  = btc_years.get(year,  "—")
        gold_v = gold_years.get(year, "—")
        print(f"  {year:<6}  {str(btc_v):>7}%  {str(gold_v):>7}%")

    print("\n=== b) Rolling 30-day Volatility → CSV ===")
    rolling = rolling_volatility()

    # Save summary
    out_path = PROCESSED / "q4_volatility.json"
    with open(out_path, "w") as f:
        json.dump(vol, f, indent=2)
    print(f"[OK] q4_volatility.json → {out_path}")