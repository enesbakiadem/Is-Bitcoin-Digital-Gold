"""
export_for_bi.py
----------------
Exports clean CSVs optimized for Power BI with German locale.
Semicolon separator, comma decimal — works with German Power BI.

Main BI outputs (data/processed/bi/)
------------------------------------
Standard CSVs:
    prices_daily.csv
    returns.csv
    rolling_volatility.csv
    drawdown_history.csv
    rolling_sharpe.csv
    seasonality.csv

Wide summary CSVs:
    normalized_1000.csv
    cagr_summary.csv
    drawdown_summary.csv
    sharpe_summary.csv
    volatility_summary.csv
    volatility_by_year.csv
    volatility_monthly.csv

Executive summary CSVs:
    executive_normalized_1000.csv
    executive_drawdown.csv
    executive_safe_haven.csv
    executive_kpis.csv

Usage
-----
    python src/export_for_bi.py
"""

import json
from pathlib import Path

import pandas as pd

from config import PROCESSED


BI = PROCESSED / "bi"
BI.mkdir(exist_ok=True)


# Full analysis asset universe after removing bonds.
ASSETS = ["BTC", "ETH", "GOLD", "ETF", "EM"]

# Focused assets for the first Power BI page.
# BTC = digital gold candidate
# GOLD = traditional safe haven
# ETF = risk-asset benchmark
EXECUTIVE_ASSETS = ["BTC", "GOLD", "ETF"]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def save_bi_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Save CSV in German Power BI friendly format:
    - semicolon separator
    - comma decimal
    - no index
    """
    df.to_csv(BI / filename, index=False, decimal=",", sep=";")
    print(f"[OK] {filename}  ({len(df)} rows)")


def read_json(filename: str) -> dict:
    path = PROCESSED / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def require_columns(df: pd.DataFrame, columns: list[str], source_name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"{source_name} is missing required columns: {missing}")


# ─────────────────────────────────────────────────────────────────────────────
# Standard CSV exports
# ─────────────────────────────────────────────────────────────────────────────
def export_standard() -> None:
    """
    Export broad analysis tables for Power BI.
    These remain useful for detailed dashboard pages.
    """
    files = {
        "prices_daily.csv": 2,
        "returns.csv": 4,
        "rolling_volatility.csv": 2,
        "drawdown_history.csv": 2,
        "rolling_sharpe.csv": 4,
        "seasonality.csv": 2,
    }

    for filename, decimals in files.items():
        path = PROCESSED / filename
        if not path.exists():
            print(f"[SKIP] {filename}")
            continue

        df = pd.read_csv(path)
        num_cols = df.select_dtypes(include="number").columns
        df[num_cols] = df[num_cols].round(decimals)

        save_bi_csv(df, filename)


# ─────────────────────────────────────────────────────────────────────────────
# Normalized performance
# ─────────────────────────────────────────────────────────────────────────────
def export_normalized() -> None:
    """
    Export wide normalized performance table.
    All assets indexed to 1000 at the first available date.
    """
    df = pd.read_csv(PROCESSED / "prices_daily.csv")
    require_columns(df, ["date", *ASSETS], "prices_daily.csv")

    out = pd.DataFrame()
    out["date"] = df["date"]

    for asset in ASSETS:
        start = df[asset].iloc[0]
        out[asset] = (df[asset] / start * 1000).round(2)

    save_bi_csv(out, "normalized_1000.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Summary exports
# ─────────────────────────────────────────────────────────────────────────────
def export_summaries() -> None:
    """
    Export summary tables from per-question JSON result files.
    """

    # ── CAGR Summary (Q2) ────────────────────────────────────────────────────
    q2 = read_json("q2_real_returns.json")

    rows = []
    for asset, data in q2.items():
        if "note" in data:
            continue

        rows.append({
            "asset": asset,
            "nominal_cagr": data["nominal_cagr_pct"],
            "real_cagr": data["real_cagr_pct"],
            "usd1000_nominal": data["usd1000_nominal_endval"],
            "usd1000_real": data["usd1000_real_endval"],
        })

    save_bi_csv(pd.DataFrame(rows), "cagr_summary.csv")

    # ── Drawdown Summary (Q5) ────────────────────────────────────────────────
    q5 = read_json("q5_drawdown.json")

    rows = []
    for asset, data in q5.items():
        rows.append({
            "asset": asset,
            "max_drawdown_pct": data["max_drawdown_pct"],
            "peak_date": data["peak_date"],
            "trough_date": data["trough_date"],
            "recovery_date": data["recovery_date"],
            "days_peak_trough": data["days_peak_to_trough"],
            "days_trough_recovery": data["days_trough_to_recovery"],
        })

    save_bi_csv(pd.DataFrame(rows), "drawdown_summary.csv")

    # ── Sharpe Summary (Q6) ──────────────────────────────────────────────────
    q6 = read_json("q6_sharpe.json")

    rows = []
    for asset, data in q6.items():
        rows.append({
            "asset": asset,
            "sharpe_full": data["sharpe_ratio"],
            "sharpe_bull21": data["by_period"]["bull_2021"],
            "sharpe_hikes22": data["by_period"]["rate_hikes"],
            "sharpe_post24": data["by_period"]["post_hikes"],
        })

    save_bi_csv(pd.DataFrame(rows), "sharpe_summary.csv")

    # ── Volatility Summary (Q4) ──────────────────────────────────────────────
    q4 = read_json("q4_volatility.json")

    rows = []
    for asset, data in q4.items():
        rows.append({
            "asset": asset,
            "ann_vol_pct": data["annualized_vol_pct"],
        })

    save_bi_csv(pd.DataFrame(rows), "volatility_summary.csv")

    # ── Volatility by Year (Q4) ──────────────────────────────────────────────
    rows = []
    for asset, data in q4.items():
        for year, vol in data["by_year"].items():
            rows.append({
                "asset": asset,
                "year": int(year),
                "ann_vol_pct": vol,
            })

    volatility_by_year = pd.DataFrame(rows).sort_values(["year", "asset"])
    save_bi_csv(volatility_by_year, "volatility_by_year.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Monthly volatility export
# ─────────────────────────────────────────────────────────────────────────────
def export_volatility_monthly() -> None:
    """
    Monthly average of 30-day rolling volatility.
    Smoother than daily, less stiff than yearly.
    Only BTC, GOLD, ETF for clarity.
    """
    df = pd.read_csv(PROCESSED / "rolling_volatility.csv")
    require_columns(
        df,
        ["date", "BTC_vol_30d", "GOLD_vol_30d", "ETF_vol_30d"],
        "rolling_volatility.csv",
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    cols = ["BTC_vol_30d", "GOLD_vol_30d", "ETF_vol_30d"]
    monthly = df[cols].resample("MS").mean().round(2).reset_index()

    monthly.columns = ["date", "BTC", "GOLD", "ETF"]

    save_bi_csv(monthly, "volatility_monthly.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Executive summary exports
# ─────────────────────────────────────────────────────────────────────────────
def export_executive_normalized() -> None:
    """
    Export long-format normalized performance for the first dashboard page.

    Output:
        date | asset | indexed_value

    This avoids Power Query unpivoting in Power BI.
    """
    df = pd.read_csv(PROCESSED / "prices_daily.csv")
    require_columns(df, ["date", *EXECUTIVE_ASSETS], "prices_daily.csv")

    out = pd.DataFrame()
    out["date"] = df["date"]

    for asset in EXECUTIVE_ASSETS:
        start = df[asset].iloc[0]
        out[asset] = (df[asset] / start * 1000).round(2)

    long = out.melt(
        id_vars="date",
        value_vars=EXECUTIVE_ASSETS,
        var_name="asset",
        value_name="indexed_value",
    )

    save_bi_csv(long, "executive_normalized_1000.csv")


def export_executive_drawdown() -> None:
    """
    Export focused drawdown table for BTC, GOLD, ETF.

    Output:
        asset | max_drawdown_pct | peak_date | trough_date | recovery_date
    """
    q5 = read_json("q5_drawdown.json")

    rows = []
    for asset in EXECUTIVE_ASSETS:
        if asset not in q5:
            raise KeyError(f"q5_drawdown.json is missing asset: {asset}")

        data = q5[asset]
        rows.append({
            "asset": asset,
            "max_drawdown_pct": data["max_drawdown_pct"],
            "peak_date": data["peak_date"],
            "trough_date": data["trough_date"],
            "recovery_date": data["recovery_date"],
            "days_peak_trough": data["days_peak_to_trough"],
            "days_trough_recovery": data["days_trough_to_recovery"],
        })

    save_bi_csv(pd.DataFrame(rows), "executive_drawdown.csv")


def export_executive_safe_haven() -> None:
    """
    Export the safe-haven test for the first dashboard page.

    Bad equity months are defined as the worst 20% of monthly ETF returns.

    Output:
        asset | avg_return_bad_equity_months | loss_vs_equity_stress_pct
              | avg_return_good_equity_months | correlation_with_equity_r
              | verdict
    """
    df = pd.read_csv(PROCESSED / "returns.csv")

    required_cols = ["ETF_return_pct"] + [f"{a}_return_pct" for a in EXECUTIVE_ASSETS]
    require_columns(df, required_cols, "returns.csv")

    low_thresh = df["ETF_return_pct"].quantile(0.20)
    high_thresh = df["ETF_return_pct"].quantile(0.80)

    bad_months = df[df["ETF_return_pct"] <= low_thresh]
    good_months = df[df["ETF_return_pct"] >= high_thresh]

    etf_bad_avg = bad_months["ETF_return_pct"].mean()
    etf_bad_loss_abs = abs(etf_bad_avg)

    rows = []

    for asset in EXECUTIVE_ASSETS:
        col = f"{asset}_return_pct"

        avg_bad = bad_months[col].mean()
        avg_good = good_months[col].mean()
        corr = df[col].corr(df["ETF_return_pct"], method="spearman")

        loss_vs_equity_stress_pct = (
            abs(avg_bad) / etf_bad_loss_abs * 100
            if etf_bad_loss_abs != 0
            else None
        )

        verdict = (
            "safe haven"
            if avg_bad > 0 and corr < 0.2
            else "not a safe haven"
            if avg_bad < -2 and corr > 0.3
            else "partial / inconclusive"
        )

        rows.append({
            "asset": asset,
            "avg_return_bad_equity_months": round(avg_bad, 2),
            "loss_vs_equity_stress_pct": round(loss_vs_equity_stress_pct, 1)
            if loss_vs_equity_stress_pct is not None
            else None,
            "avg_return_good_equity_months": round(avg_good, 2),
            "correlation_with_equity_r": round(corr, 4),
            "verdict": verdict,
            "equity_bad_threshold_pct": round(low_thresh, 2),
            "equity_good_threshold_pct": round(high_thresh, 2),
            "n_bad_months": len(bad_months),
            "n_good_months": len(good_months),
        })

    save_bi_csv(pd.DataFrame(rows), "executive_safe_haven.csv")


def export_executive_kpis() -> None:
    """
    Export four hand-picked KPI cards for the executive summary page.

    Output:
        metric | value | display_value | note | accent_group

    Important:
    display_value is intentionally formatted as text so Power BI does not
    auto-convert correlations or percentages into unwanted numeric formats.
    """
    q1 = read_json("q1_correlation.json")
    q5 = read_json("q5_drawdown.json")

    full = q1["full"]

    btc_gold_corr = full["BTC_vs_GOLD"]["spearman_r"]
    btc_etf_corr = full["BTC_vs_ETF"]["spearman_r"]

    btc_drawdown = q5["BTC"]["max_drawdown_pct"]
    gold_drawdown = q5["GOLD"]["max_drawdown_pct"]

    rows = [
        {
            "metric": "BTC vs Gold correlation",
            "value": btc_gold_corr,
            "display_value": f"r = {btc_gold_corr:.2f}",
            "note": "weak relationship",
            "accent_group": "gold",
        },
        {
            "metric": "BTC vs Equity correlation",
            "value": btc_etf_corr,
            "display_value": f"r = {btc_etf_corr:.2f}",
            "note": "stronger than gold",
            "accent_group": "equity",
        },
        {
            "metric": "Bitcoin max drawdown",
            "value": btc_drawdown,
            "display_value": f"−{abs(btc_drawdown):.0f}%",
            "note": "peak-to-trough loss",
            "accent_group": "bitcoin",
        },
        {
            "metric": "Gold max drawdown",
            "value": gold_drawdown,
            "display_value": f"−{abs(gold_drawdown):.0f}%",
            "note": "far shallower",
            "accent_group": "gold",
        },
    ]

    df = pd.DataFrame(rows)

    # Force display_value to stay text before export.
    df["display_value"] = df["display_value"].astype(str)

    save_bi_csv(df, "executive_kpis.csv")


def export_executive_summary() -> None:
    """
    Export all focused CSVs needed for the first Power BI page.
    """
    export_executive_normalized()
    export_executive_drawdown()
    export_executive_safe_haven()
    export_executive_kpis()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    export_standard()
    export_normalized()
    export_summaries()
    export_volatility_monthly()
    export_executive_summary()

    print(f"\nDone — load from: data/processed/bi/")
    print("Trennzeichen: Semikolon | Dezimal: Komma")