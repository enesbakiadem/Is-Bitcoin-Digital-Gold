"""
q6_sharpe.py
------------
Q6 — Which asset delivered the best return per unit of risk?

Sharpe Ratio = (Asset Return - Risk-Free Rate) / Volatility

In plain terms: how much return did you get for every percentage
point of risk you took on? Higher = more efficient.

Example:
  BTC CAGR 27%, Volatility 66% → you took on a lot of risk
  GOLD CAGR 16%, Volatility 16% → much less risk for decent return
  Who was more "efficient"? Sharpe tells you.

Risk-free rate: we use the average Fed Funds Rate over the period.
This is standard practice — it represents what you could have earned
risk-free (e.g. in a money market fund).

Two versions:
  a) Overall Sharpe — full period
  b) Rolling 12-month Sharpe → CSV for Power BI
     Shows when each asset was efficient and when it wasn't.

Usage
------
    python src/q6_sharpe.py
"""

import json
import pandas as pd
import numpy as np
from config import F_RETURNS, F_MASTER, PROCESSED, TICKERS

# ── Load data ─────────────────────────────────────────────────────────────────
returns = pd.read_csv(F_RETURNS, index_col="date", parse_dates=True)
master  = pd.read_csv(F_MASTER,  index_col="date", parse_dates=True)

ASSETS        = list(TICKERS.keys())
TRADING_DAYS  = 252

# Monthly risk-free rate from Fed Funds Rate
macro_m       = master[["FED_FUNDS"]].resample("MS").last()
avg_rf_annual = macro_m["FED_FUNDS"].mean()          # annual %
avg_rf_monthly = avg_rf_annual / 12                  # monthly %


# ─────────────────────────────────────────────────────────────────────────────
# a) Overall Sharpe Ratio
# ─────────────────────────────────────────────────────────────────────────────
def overall_sharpe() -> dict:
    """
    Annualized Sharpe Ratio for each asset over the full period.

    Annualized Sharpe = (mean monthly excess return / std monthly return)
                        * sqrt(12)

    Excess return = asset return - risk-free rate (Fed Funds / 12)
    """
    results = {}
    for asset in ASSETS:
        col = f"{asset}_return_pct"
        ret = returns[col].dropna()

        excess        = ret - avg_rf_monthly
        sharpe_annual = (excess.mean() / excess.std()) * np.sqrt(12)

        # Also compute for specific periods
        def period_sharpe(start, end):
            s = ret.loc[start:end]
            if len(s) < 6:
                return None
            e = s - avg_rf_monthly
            return round((e.mean() / e.std()) * np.sqrt(12), 4)

        results[asset] = {
            "sharpe_ratio":        round(sharpe_annual, 4),
            "avg_monthly_return":  round(ret.mean(), 4),
            "monthly_std":         round(ret.std(),  4),
            "risk_free_rate_ann":  round(avg_rf_annual, 4),
            "by_period": {
                "bull_2021":   period_sharpe("2020-06-01", "2022-01-01"),
                "rate_hikes":  period_sharpe("2022-01-01", "2023-12-01"),
                "post_hikes":  period_sharpe("2024-01-01", "2026-05-01"),
            }
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# b) Rolling 12-month Sharpe → CSV for Power BI
# ─────────────────────────────────────────────────────────────────────────────
def rolling_sharpe() -> pd.DataFrame:
    """
    12-month rolling Sharpe Ratio for each asset.
    Window of 12 months gives stable estimates without being too slow.
    """
    rolling = pd.DataFrame(index=returns.index)

    for asset in ASSETS:
        col = f"{asset}_return_pct"
        ret = returns[col]
        excess = ret - avg_rf_monthly

        rolling[f"{asset}_sharpe_12m"] = (
            excess.rolling(12).mean() / excess.rolling(12).std() * np.sqrt(12)
        ).round(4)

    out_path = PROCESSED / "rolling_sharpe.csv"
    rolling.to_csv(out_path)
    print(f"[OK] rolling_sharpe.csv  ({len(rolling)} rows) → {out_path}")
    return rolling


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print(f"\n  Risk-free rate used: {round(avg_rf_annual, 2)}% p.a. (avg Fed Funds Rate)")

    print("\n=== a) Overall Sharpe Ratio ===")
    results = overall_sharpe()

    print(f"\n  {'Asset':<6}  {'Sharpe':>8}  {'Avg ret/mo':>12}  {'Std/mo':>8}  {'Bull 21':>9}  {'Hikes 22':>9}  {'Post 24':>9}")
    print("  " + "-" * 75)
    for asset, r in sorted(results.items(), key=lambda x: -x[1]["sharpe_ratio"]):
        bp = r["by_period"]
        print(
            f"  {asset:<6}  "
            f"{r['sharpe_ratio']:>8.4f}  "
            f"{r['avg_monthly_return']:>11.4f}%  "
            f"{r['monthly_std']:>7.4f}%  "
            f"{str(bp['bull_2021']):>9}  "
            f"{str(bp['rate_hikes']):>9}  "
            f"{str(bp['post_hikes']):>9}"
        )

    print("\n=== b) Rolling 12-month Sharpe → CSV ===")
    rolling_sharpe()

    # Save
    out_path = PROCESSED / "q6_sharpe.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] q6_sharpe.json → {out_path}")