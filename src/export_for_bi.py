"""
export_for_bi.py
----------------
Exports the focused CSV files used by the Power BI executive dashboard.

The script assumes that the analysis scripts have already created:
- prices_daily.csv
- returns.csv
- q1_correlation.json
- q3_digital_gold.json
- q5_drawdown.json

Outputs are written to:
data/processed/bi/

CSV format:
- semicolon separator
- comma decimal
- no index
"""

import json
from pathlib import Path

import pandas as pd

from config import PROCESSED


BI = PROCESSED / "bi"
BI.mkdir(parents=True, exist_ok=True)

ASSETS = ["BTC", "GOLD", "ETF"]


def save_bi_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(BI / filename, index=False, sep=";", decimal=",")
    print(f"[OK] {filename} ({len(df)} rows)")


def read_json(filename: str) -> dict:
    path = PROCESSED / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def require_columns(df: pd.DataFrame, columns: list[str], source_name: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"{source_name} is missing required columns: {missing}")


def export_executive_normalized() -> None:
    """
    Long-format indexed performance table.

    Output:
    date | asset | indexed_value
    """
    df = pd.read_csv(PROCESSED / "prices_daily.csv")
    require_columns(df, ["date", *ASSETS], "prices_daily.csv")

    normalized = pd.DataFrame({"date": df["date"]})

    for asset in ASSETS:
        start_value = df[asset].iloc[0]
        normalized[asset] = (df[asset] / start_value * 1000).round(2)

    out = normalized.melt(
        id_vars="date",
        value_vars=ASSETS,
        var_name="asset",
        value_name="indexed_value",
    )

    save_bi_csv(out, "executive_normalized_1000.csv")


def export_executive_drawdown() -> None:
    """
    Maximum drawdown summary.

    Output:
    asset | max_drawdown_pct | peak_date | trough_date | recovery_date
    """
    q5 = read_json("q5_drawdown.json")

    rows = []
    for asset in ASSETS:
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
    Safe-haven behavior during bad equity months.

    Bad equity months are defined as the worst 20% of ETF monthly returns.

    Output:
    asset | avg_return_bad_equity_months | avg_return_good_equity_months
          | correlation_with_equity_r | verdict
    """
    df = pd.read_csv(PROCESSED / "returns.csv")

    required = ["ETF_return_pct"] + [f"{asset}_return_pct" for asset in ASSETS]
    require_columns(df, required, "returns.csv")

    low_threshold = df["ETF_return_pct"].quantile(0.20)
    high_threshold = df["ETF_return_pct"].quantile(0.80)

    bad_months = df[df["ETF_return_pct"] <= low_threshold]
    good_months = df[df["ETF_return_pct"] >= high_threshold]

    rows = []

    for asset in ASSETS:
        return_col = f"{asset}_return_pct"

        avg_bad = bad_months[return_col].mean()
        avg_good = good_months[return_col].mean()
        corr = df[return_col].corr(df["ETF_return_pct"], method="spearman")

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
            "avg_return_good_equity_months": round(avg_good, 2),
            "correlation_with_equity_r": round(corr, 4),
            "verdict": verdict,
            "equity_bad_threshold_pct": round(low_threshold, 2),
            "equity_good_threshold_pct": round(high_threshold, 2),
            "n_bad_months": len(bad_months),
            "n_good_months": len(good_months),
        })

    save_bi_csv(pd.DataFrame(rows), "executive_safe_haven.csv")


def export_executive_kpis() -> None:
    """
    KPI cards for the executive dashboard.

    Output:
    metric | value | display_value | note | accent_group
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
            "note": "near zero",
            "accent_group": "gold",
        },
        {
            "metric": "BTC vs Equity correlation",
            "value": btc_etf_corr,
            "display_value": f"r = {btc_etf_corr:.2f}",
            "note": "modest, but higher",
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

    save_bi_csv(pd.DataFrame(rows), "executive_kpis.csv")


def export_executive_correlation_full() -> None:
    """
    Full-period BTC correlation comparison.

    Output:
    pair_label | spearman_r | p_value | display_value | note | accent_group | sort_order
    """
    q1 = read_json("q1_correlation.json")
    full = q1["full"]

    btc_gold_r = full["BTC_vs_GOLD"]["spearman_r"]
    btc_gold_p = full["BTC_vs_GOLD"]["p_value"]

    btc_etf_r = full["BTC_vs_ETF"]["spearman_r"]
    btc_etf_p = full["BTC_vs_ETF"]["p_value"]

    rows = [
        {
            "pair_label": "BTC vs Equity",
            "spearman_r": btc_etf_r,
            "p_value": btc_etf_p,
            "display_value": f"r = {btc_etf_r:.2f}",
            "note": "modest, but higher",
            "accent_group": "equity",
            "sort_order": 1,
        },
        {
            "pair_label": "BTC vs Gold",
            "spearman_r": btc_gold_r,
            "p_value": btc_gold_p,
            "display_value": f"r = {btc_gold_r:.2f}",
            "note": "near zero",
            "accent_group": "gold",
            "sort_order": 2,
        },
    ]

    save_bi_csv(pd.DataFrame(rows), "executive_correlation_full.csv")


def export_executive_scorecard() -> None:
    """
    Final Digital Gold scorecard.

    Output:
    test | result | verdict | accent_group | sort_order
    """
    rows = [
        {
            "test": "Fixed supply narrative",
            "result": "Pass",
            "verdict": "Bitcoin has a hard supply cap.",
            "accent_group": "pass",
            "sort_order": 1,
        },
        {
            "test": "Inflation hedge behavior",
            "result": "Inconclusive",
            "verdict": "No clear monthly inflation hedge behavior.",
            "accent_group": "neutral",
            "sort_order": 2,
        },
        {
            "test": "Safe haven behavior",
            "result": "Fail",
            "verdict": "BTC fell in bad equity months while Gold stayed flat.",
            "accent_group": "fail",
            "sort_order": 3,
        },
        {
            "test": "Gold-like correlation",
            "result": "Fail",
            "verdict": "BTC-Gold correlation was near zero.",
            "accent_group": "fail",
            "sort_order": 4,
        },
        {
            "test": "Drawdown profile",
            "result": "Fail",
            "verdict": "BTC drawdowns were much deeper than Gold.",
            "accent_group": "fail",
            "sort_order": 5,
        },
        {
            "test": "Return profile",
            "result": "Strong",
            "verdict": "BTC delivered the highest upside, but with much higher risk.",
            "accent_group": "pass",
            "sort_order": 6,
        },
    ]

    save_bi_csv(pd.DataFrame(rows), "executive_scorecard.csv")


def export_executive_summary() -> None:
    export_executive_normalized()
    export_executive_drawdown()
    export_executive_safe_haven()
    export_executive_kpis()
    export_executive_correlation_full()
    export_executive_scorecard()


if __name__ == "__main__":
    export_executive_summary()

    print("\nDone — load from: data/processed/bi/")
    print("Trennzeichen: Semikolon | Dezimal: Komma")