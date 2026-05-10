"""
load_to_sqlite.py
-----------------
Loads all processed CSVs into a single SQLite database.
This allows SQL-based analysis alongside the Python pipeline.

Tables created
--------------
  prices_daily       : daily closing prices, all assets
  macro_monthly      : CPI, Fed Funds Rate, monthly
  returns_monthly    : nominal + real returns, monthly
  rolling_volatility : 30-day rolling annualized volatility, daily
  drawdown_history   : daily drawdown from ATH, all assets
  seasonality        : avg return + hit rate by month per asset

Usage
------
    python src/load_to_sqlite.py
Then open data/processed/assets.db in DB Browser for SQLite.
"""

import sqlite3
import pandas as pd
from config import PROCESSED

DB_PATH = PROCESSED / "assets.db"

TABLES = {
    "prices_daily":       PROCESSED / "prices_daily.csv",
    "macro_monthly":      PROCESSED / "macro_monthly.csv",
    "returns_monthly":    PROCESSED / "returns.csv",
    "rolling_volatility": PROCESSED / "rolling_volatility.csv",
    "drawdown_history":   PROCESSED / "drawdown_history.csv",
    "seasonality":        PROCESSED / "seasonality.csv",
}


def load_all():
    conn = sqlite3.connect(DB_PATH)

    for table, path in TABLES.items():
        if not path.exists():
            print(f"[SKIP] {path.name} not found")
            continue
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"[OK]   {table:<25} ({len(df):>5} rows)")

    conn.close()
    print(f"\nDatabase → {DB_PATH}")
    print("Open with: DB Browser for SQLite")


if __name__ == "__main__":
    load_all()