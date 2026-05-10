"""
q2_real_returns.py
------------------
Q2 — Who actually grew your purchasing power since 2015?

Compares BTC, Gold, and World ETF on:
  - Nominal total return and CAGR
  - Real (inflation-adjusted) total return and CAGR
  - $1000 invested at start → worth how much today, in real terms?

Method:
  Real return = deflate monthly prices by CPI index, then compute
  the same metrics as nominal. This strips out the effect of
  inflation so we see actual purchasing power gained.

  CAGR (Compound Annual Growth Rate):
  CAGR = (end / start) ^ (1 / years) - 1
  Tells you the equivalent steady annual return over the period.

Usage
------
    python src/q2_real_returns.py
"""

import json
import pandas as pd
from config import F_MASTER, PROCESSED

# ── Load data ─────────────────────────────────────────────────────────────────
master = pd.read_csv(F_MASTER, index_col="date", parse_dates=True)

# Monthly prices (cleaner for CAGR)
monthly = master[["BTC", "GOLD", "ETF", "CPI_indexed"]].resample("MS").last()


# ─────────────────────────────────────────────────────────────────────────────
def calc_returns(series: pd.Series, cpi: pd.Series, label: str) -> dict:
    """
    Computes nominal and real CAGR + total return for a single asset.
    Also computes what $1000 invested at start is worth today, real terms.
    """
    # Align on common dates
    common = series.index.intersection(cpi.index)
    s   = series.loc[common].dropna()
    c   = cpi.loc[common].dropna()
    common = s.index.intersection(c.index)
    s, c = s.loc[common], c.loc[common]

    if len(s) < 12:
        return {"note": "insufficient data"}

    n_years = (s.index[-1] - s.index[0]).days / 365.25

    # Nominal
    nom_total = (s.iloc[-1] / s.iloc[0] - 1) * 100
    nom_cagr  = ((s.iloc[-1] / s.iloc[0]) ** (1 / n_years) - 1) * 100

    # Real — deflate by CPI
    real_s      = s / c * c.iloc[0]   # express in start-date dollars
    real_total  = (real_s.iloc[-1] / real_s.iloc[0] - 1) * 100
    real_cagr   = ((real_s.iloc[-1] / real_s.iloc[0]) ** (1 / n_years) - 1) * 100

    # $1000 invested
    invested       = 1000
    nom_end_value  = invested * (s.iloc[-1] / s.iloc[0])
    real_end_value = invested * (real_s.iloc[-1] / real_s.iloc[0])

    return {
        "asset":                  label,
        "start_date":             str(s.index[0].date()),
        "end_date":               str(s.index[-1].date()),
        "n_years":                round(n_years, 1),
        "start_price_usd":        round(float(s.iloc[0]), 2),
        "end_price_usd":          round(float(s.iloc[-1]), 2),
        "nominal_total_pct":      round(nom_total, 1),
        "nominal_cagr_pct":       round(nom_cagr, 2),
        "real_total_pct":         round(real_total, 1),
        "real_cagr_pct":          round(real_cagr, 2),
        "usd1000_nominal_endval": round(float(nom_end_value), 2),
        "usd1000_real_endval":    round(float(real_end_value), 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    cpi = monthly["CPI_indexed"].dropna()

    results = {}
    for asset in ["BTC", "GOLD", "ETF"]:
        results[asset] = calc_returns(monthly[asset], cpi, asset)

    # Print
    print(f"\n{'Asset':<6}  {'Nom. CAGR':>10}  {'Real CAGR':>10}  {'$1000 → (nominal)':>18}  {'$1000 → (real)':>15}")
    print("-" * 70)
    for asset, r in results.items():
        if "note" in r:
            print(f"{asset:<6}  {r['note']}")
            continue
        print(
            f"{asset:<6}  "
            f"{r['nominal_cagr_pct']:>9.2f}%  "
            f"{r['real_cagr_pct']:>9.2f}%  "
            f"${r['usd1000_nominal_endval']:>17,.2f}  "
            f"${r['usd1000_real_endval']:>14,.2f}"
        )

    print(f"\nInflation eroded ~{round((1 - 1/(cpi.iloc[-1]/100)) * 100, 1)}% of purchasing power over the period.")

    # Save
    out_path = PROCESSED / "q2_real_returns.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Saved → {out_path}")