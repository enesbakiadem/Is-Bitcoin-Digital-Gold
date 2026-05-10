"""
q2_real_returns.py
------------------
Q2 — Who actually grew your purchasing power since 2017?

Compares all six assets on:
  - Nominal total return and CAGR
  - Real (inflation-adjusted) total return and CAGR
  - $1,000 invested at start → worth how much today, real terms?

Method:
  Real return = deflate monthly prices by CPI index, then compute
  the same metrics as nominal. This strips out inflation so we see
  actual purchasing power gained.

  CAGR (Compound Annual Growth Rate):
  CAGR = (end / start) ^ (1 / years) - 1
  Equivalent steady annual return over the full period.

  Real CAGR uses CPI-deflated prices — same formula, real values.

Usage
------
    python src/q2_real_returns.py
"""

import json
import pandas as pd
from config import F_MASTER, PROCESSED, TICKERS

# ── Load data ─────────────────────────────────────────────────────────────────
master  = pd.read_csv(F_MASTER, index_col="date", parse_dates=True)
monthly = master[list(TICKERS.keys()) + ["CPI_indexed"]].resample("MS").last()


# ─────────────────────────────────────────────────────────────────────────────
def calc_returns(asset: str) -> dict:
    """
    Nominal and real CAGR + total return for a single asset.
    $1,000 scenario in both nominal and real terms.
    """
    s   = monthly[asset].dropna()
    cpi = monthly["CPI_indexed"].dropna()

    common = s.index.intersection(cpi.index)
    s, cpi = s.loc[common], cpi.loc[common]

    if len(s) < 12:
        return {"note": "insufficient data"}

    n_years = (s.index[-1] - s.index[0]).days / 365.25

    # Nominal
    nom_total = (s.iloc[-1] / s.iloc[0] - 1) * 100
    nom_cagr  = ((s.iloc[-1] / s.iloc[0]) ** (1 / n_years) - 1) * 100

    # Real — deflate by CPI
    real_s     = s / cpi * cpi.iloc[0]
    real_total = (real_s.iloc[-1] / real_s.iloc[0] - 1) * 100
    real_cagr  = ((real_s.iloc[-1] / real_s.iloc[0]) ** (1 / n_years) - 1) * 100

    # $1,000 scenario
    nom_end  = 1000 * (s.iloc[-1] / s.iloc[0])
    real_end = 1000 * (real_s.iloc[-1] / real_s.iloc[0])

    return {
        "asset":                  asset,
        "start_date":             str(s.index[0].date()),
        "end_date":               str(s.index[-1].date()),
        "n_years":                round(n_years, 1),
        "start_price_usd":        round(float(s.iloc[0]), 2),
        "end_price_usd":          round(float(s.iloc[-1]), 2),
        "nominal_total_pct":      round(nom_total, 1),
        "nominal_cagr_pct":       round(nom_cagr, 2),
        "real_total_pct":         round(real_total, 1),
        "real_cagr_pct":          round(real_cagr, 2),
        "usd1000_nominal_endval": round(float(nom_end), 2),
        "usd1000_real_endval":    round(float(real_end), 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    results = {}
    for asset in TICKERS.keys():
        results[asset] = calc_returns(asset)

    # Inflation info
    cpi = monthly["CPI_indexed"].dropna()
    inflation_eroded = round((1 - 1 / (cpi.iloc[-1] / 100)) * 100, 1)

    # Print table
    print(f"\n{'Asset':<6}  {'Nom. CAGR':>10}  {'Real CAGR':>10}  {'$1000 nominal':>15}  {'$1000 real':>12}")
    print("-" * 60)
    for asset, r in results.items():
        if "note" in r:
            print(f"{asset:<6}  {r['note']}")
            continue
        print(
            f"{asset:<6}  "
            f"{r['nominal_cagr_pct']:>9.2f}%  "
            f"{r['real_cagr_pct']:>9.2f}%  "
            f"${r['usd1000_nominal_endval']:>14,.2f}  "
            f"${r['usd1000_real_endval']:>11,.2f}"
        )

    print(f"\nInflation eroded ~{inflation_eroded}% of purchasing power over the period.")
    print(f"$1,000 in cash → ${round(1000 * (1 - inflation_eroded/100), 0):.0f} real value today.")

    # Save
    out_path = PROCESSED / "q2_real_returns.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Saved → {out_path}")