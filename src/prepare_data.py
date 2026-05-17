"""
prepare_data.py
---------------
Downloads and cleans all data for the asset comparison analysis.

Sources
-------
- Yahoo Finance (via yfinance) : BTC, ETH, GLD, ACWI, EEM — daily close
- FRED API (via fredapi)       : US CPI, Fed Funds Rate — monthly

Key design decisions
---------------------
- Trading days only: no forward-fill across weekends/holidays.
  Forward-filling non-trading days inflates correlation between assets
  with different trading schedules (e.g. BTC trades 7 days, stocks 5 days).
  Solution: inner join on dates where ALL assets have real prices.
- All prices in USD.
- FRED API key loaded from .env — never hardcoded.

Outputs (data/processed/)
--------------------------
- prices_daily.csv   : daily close, trading days only, all assets
- macro_monthly.csv  : CPI index + Fed Funds Rate, monthly
- returns.csv        : monthly returns, nominal + real
- master.csv         : prices + macro merged, analysis-ready

Usage
------
    python src/prepare_data.py
"""

import pandas as pd
import yfinance as yf
from fredapi import Fred
from config import (
    PROCESSED, TICKERS, FRED_SERIES, FRED_API_KEY,
    START_DATE, END_DATE,
    F_PRICES, F_MACRO, F_RETURNS, F_MASTER,
)

PROCESSED.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Asset prices — Yahoo Finance
# ─────────────────────────────────────────────────────────────────────────────
def load_prices() -> pd.DataFrame:
    """
    Downloads daily adjusted close prices for all tickers.

    Trading days only — no forward-fill.
    Uses inner join so only dates where ALL assets have a real price are kept.
    This avoids correlation inflation from interpolated weekend values.

    BTC and ETH trade 7 days/week; traditional assets trade Mon–Fri.
    After inner join, the effective calendar is Mon–Fri (stock market days).
    """
    frames = {}
    for name, ticker in TICKERS.items():
        print(f"  Downloading {name} ({ticker})...")
        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
        )
        if df.empty:
            raise ValueError(f"No data returned for {ticker}. Check ticker or internet connection.")
        frames[name] = df["Close"].squeeze()

    # Inner join — only real trading days shared by all assets
    prices = pd.concat(frames, axis=1, join="inner")
    prices.index = pd.to_datetime(prices.index)
    prices.index.name = "date"
    prices.columns = list(TICKERS.keys())

    prices.to_csv(F_PRICES)
    print(f"[OK] {F_PRICES.name}  ({len(prices)} rows, {prices.shape[1]} assets)")
    print(f"     Date range: {prices.index[0].date()} → {prices.index[-1].date()}")
    return prices


# ─────────────────────────────────────────────────────────────────────────────
# 2. Macro data — FRED
# ─────────────────────────────────────────────────────────────────────────────
def load_macro() -> pd.DataFrame:
    """
    Downloads monthly CPI and Fed Funds Rate from FRED.

    CPI (CPIAUCSL): used to compute inflation and deflate nominal returns.
    Fed Funds Rate (FEDFUNDS): proxy for monetary policy tightness.

    CPI_indexed: normalized to 100 at START_DATE for readability.
    inflation_yoy: year-over-year % change in CPI.
    """
    fred = Fred(api_key=FRED_API_KEY)

    series = {}
    for name, series_id in FRED_SERIES.items():
        print(f"  Downloading {name} ({series_id})...")
        s = fred.get_series(series_id, observation_start=START_DATE, observation_end=END_DATE)
        s.index = pd.to_datetime(s.index)
        series[name] = s

    macro = pd.DataFrame(series)
    macro.index.name = "date"
    macro = macro.resample("MS").last()

    macro["CPI_indexed"]    = macro["CPI"] / macro["CPI"].iloc[0] * 100
    macro["inflation_yoy"]  = macro["CPI"].pct_change(12) * 100

    macro.to_csv(F_MACRO)
    print(f"[OK] {F_MACRO.name}  ({len(macro)} rows)")
    return macro


# ─────────────────────────────────────────────────────────────────────────────
# 3. Returns — nominal + real
# ─────────────────────────────────────────────────────────────────────────────
def build_returns(prices: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly returns for each asset, nominal and inflation-adjusted.

    Nominal: simple % change month-over-month.
    Real: (1 + nominal) / (1 + monthly_inflation) - 1

    Cumulative index (base 100 at start) for Power BI performance charts.
    """
    monthly = prices.resample("MS").last()

    returns = monthly.pct_change() * 100
    returns.columns = [f"{c}_return_pct" for c in monthly.columns]

    # Monthly CPI inflation
    cpi_aligned      = macro["CPI"].reindex(monthly.index, method="ffill")
    inflation_monthly = cpi_aligned.pct_change() * 100

    # Real returns
    for asset in TICKERS.keys():
        nom_col = f"{asset}_return_pct"
        returns[f"{asset}_real_return_pct"] = (
            ((1 + returns[nom_col] / 100) / (1 + inflation_monthly / 100) - 1) * 100
        )

    # Cumulative performance index
    for asset in TICKERS.keys():
        nom_col = f"{asset}_return_pct"
        returns[f"{asset}_cumulative"] = (1 + returns[nom_col] / 100).cumprod() * 100

    returns.index.name = "date"
    returns.to_csv(F_RETURNS)
    print(f"[OK] {F_RETURNS.name}  ({len(returns)} rows)")
    return returns


# ─────────────────────────────────────────────────────────────────────────────
# 4. Master merge
# ─────────────────────────────────────────────────────────────────────────────
def build_master(prices: pd.DataFrame, macro: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    """
    Merges daily prices with monthly macro (forward-filled to daily).
    Forward-fill is safe here: macro data is legitimately monthly,
    not a workaround for missing trading days.
    """
    macro_daily   = macro.resample("D").last().ffill()
    returns_daily = returns.resample("D").last().ffill()

    master = prices.copy()
    master = master.join(macro_daily[["CPI_indexed", "inflation_yoy", "FED_FUNDS"]], how="left")
    master = master.join(returns_daily, how="left")

    master.index.name = "date"
    master.to_csv(F_MASTER)
    print(f"[OK] {F_MASTER.name}  ({len(master)} rows, {master.shape[1]} columns)")
    return master


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Downloading asset prices...")
    prices = load_prices()

    print("\nDownloading macro data...")
    macro = load_macro()

    print("\nBuilding returns...")
    returns = build_returns(prices, macro)

    print("\nBuilding master...")
    master = build_master(prices, macro, returns)

    print("\nPreview — last 5 rows:")
    cols = ["BTC", "ETH", "GOLD", "ETF", "EM", "inflation_yoy", "FED_FUNDS"]
    print(master.tail(5)[cols].round(2).to_string())