"""
export_for_bi.py
----------------
Exports clean CSVs optimized for Power BI with German locale.
Semicolon separator, comma decimal — works with German Power BI.

Outputs (data/processed/bi/)
-----------------------------
Standard CSVs: prices_daily, returns, rolling_volatility,
               drawdown_history, rolling_sharpe, seasonality
Normalized:    normalized_1000  — all assets indexed to 1000 at start
Summaries:     cagr_summary, drawdown_summary, sharpe_summary,
               volatility_summary — ready for bar charts in Power BI

Usage
------
    python src/export_for_bi.py
"""

import json
import pandas as pd
from config import PROCESSED

BI = PROCESSED / "bi"
BI.mkdir(exist_ok=True)

ASSETS = ["BTC", "ETH", "GOLD", "ETF", "EM", "BOND"]


def export_standard():
    files = {
        "prices_daily.csv":       2,
        "returns.csv":            4,
        "rolling_volatility.csv": 2,
        "drawdown_history.csv":   2,
        "rolling_sharpe.csv":     4,
        "seasonality.csv":        2,
    }
    for filename, decimals in files.items():
        path = PROCESSED / filename
        if not path.exists():
            print(f"[SKIP] {filename}")
            continue
        df = pd.read_csv(path)
        num_cols = df.select_dtypes(include="number").columns
        df[num_cols] = df[num_cols].round(decimals)
        df.to_csv(BI / filename, index=False, decimal=",", sep=";")
        print(f"[OK] {filename}")


def export_normalized():
    df = pd.read_csv(PROCESSED / "prices_daily.csv")
    out = pd.DataFrame()
    out["date"] = df["date"]
    for asset in ASSETS:
        start = df[asset].iloc[0]
        out[f"{asset}"] = (df[asset] / start * 1000).round(2)
    out.to_csv(BI / "normalized_1000.csv", index=False, decimal=",", sep=";")
    print(f"[OK] normalized_1000.csv  ({len(out)} rows)")


def export_summaries():
    # ── CAGR Summary (Q2) ────────────────────────────────────────────────────
    with open(PROCESSED / "q2_real_returns.json") as f:
        q2 = json.load(f)
    rows = []
    for asset, data in q2.items():
        if "note" in data:
            continue
        rows.append({
            "asset":           asset,
            "nominal_cagr":    data["nominal_cagr_pct"],
            "real_cagr":       data["real_cagr_pct"],
            "usd1000_nominal": data["usd1000_nominal_endval"],
            "usd1000_real":    data["usd1000_real_endval"],
        })
    pd.DataFrame(rows).to_csv(BI / "cagr_summary.csv", index=False, decimal=",", sep=";")
    print(f"[OK] cagr_summary.csv")

    # ── Drawdown Summary (Q5) ────────────────────────────────────────────────
    with open(PROCESSED / "q5_drawdown.json") as f:
        q5 = json.load(f)
    rows = []
    for asset, data in q5.items():
        rows.append({
            "asset":              asset,
            "max_drawdown_pct":   data["max_drawdown_pct"],
            "peak_date":          data["peak_date"],
            "trough_date":        data["trough_date"],
            "recovery_date":      data["recovery_date"],
            "days_peak_trough":   data["days_peak_to_trough"],
            "days_trough_recovery": data["days_trough_to_recovery"],
        })
    pd.DataFrame(rows).to_csv(BI / "drawdown_summary.csv", index=False, decimal=",", sep=";")
    print(f"[OK] drawdown_summary.csv")

    # ── Sharpe Summary (Q6) ──────────────────────────────────────────────────
    with open(PROCESSED / "q6_sharpe.json") as f:
        q6 = json.load(f)
    rows = []
    for asset, data in q6.items():
        rows.append({
            "asset":          asset,
            "sharpe_full":    data["sharpe_ratio"],
            "sharpe_bull21":  data["by_period"]["bull_2021"],
            "sharpe_hikes22": data["by_period"]["rate_hikes"],
            "sharpe_post24":  data["by_period"]["post_hikes"],
        })
    pd.DataFrame(rows).to_csv(BI / "sharpe_summary.csv", index=False, decimal=",", sep=";")
    print(f"[OK] sharpe_summary.csv")

    # ── Volatility Summary (Q4) ──────────────────────────────────────────────
    with open(PROCESSED / "q4_volatility.json") as f:
        q4 = json.load(f)
    rows = []
    for asset, data in q4.items():
        rows.append({
            "asset":       asset,
            "ann_vol_pct": data["annualized_vol_pct"],
        })
    pd.DataFrame(rows).to_csv(BI / "volatility_summary.csv", index=False, decimal=",", sep=";")
    print(f"[OK] volatility_summary.csv")


if __name__ == "__main__":
    export_standard()
    export_normalized()
    export_summaries()
    print(f"\nDone — load from: data/processed/bi/")
    print("Trennzeichen: Semikolon | Dezimal: Komma")