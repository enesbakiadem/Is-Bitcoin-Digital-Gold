"""
prepare_data.py
---------------
Downloads and cleans all data for the asset comparison analysis.

Sources
-------
- Yahoo Finance (via yfinance): BTC-USD, GLD, ACWI — daily close prices
- FRED API (via fredapi): US CPI, Fed Funds Rate — monthly

Outputs (written to data/processed/)
--------------------------------------
- prices_daily.csv    : daily closing prices in USD, all three assets
- macro_monthly.csv   : CPI index + Fed Funds Rate, monthly
- returns.csv         : monthly returns (nominal + real) for all assets
- master.csv          : prices + macro merged, analysis-ready

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
    Downloads daily adjusted close prices for BTC, GLD, ACWI.
    All prices in USD. Missing trading days (weekends/holidays) are
    forward-filled so all three assets share a continuous daily index.
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
            raise ValueError(f"No data returned for {ticker}. Check ticker or date range.")
        frames[name] = df["Close"].squeeze()

    prices = pd.DataFrame(frames)
    prices.index.name = "date"
    prices.index = pd.to_datetime(prices.index)

    # Forward-fill weekends/holidays so all assets align on same calendar days
    prices = prices.resample("D").last().ffill()
    prices = prices.loc[START_DATE:END_DATE]

    prices.to_csv(F_PRICES)
    print(f"[OK] {F_PRICES.name}  ({len(prices)} rows, {prices.shape[1]} assets)")
    return prices


# ─────────────────────────────────────────────────────────────────────────────
# 2. Macro data — FRED
# ─────────────────────────────────────────────────────────────────────────────
def load_macro() -> pd.DataFrame:
    """
    Downloads monthly CPI and Fed Funds Rate from FRED.

    CPI (CPIAUCSL): used to compute inflation and deflate nominal returns.
    Fed Funds Rate (FEDFUNDS): effective overnight rate, proxy for monetary policy.

    Both are monthly. Indexed to CPI = 100 at START_DATE for easier interpretation.
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
    macro = macro.resample("MS").last()  # month-start frequency

    # CPI index: normalize to 100 at start date for readability
    macro["CPI_indexed"] = macro["CPI"] / macro["CPI"].iloc[0] * 100

    # Monthly inflation rate (YoY %)
    macro["inflation_yoy"] = macro["CPI"].pct_change(12) * 100

    macro.to_csv(F_MACRO)
    print(f"[OK] {F_MACRO.name}  ({len(macro)} rows)")
    return macro


# ─────────────────────────────────────────────────────────────────────────────
# 3. Returns — nominal + real
# ─────────────────────────────────────────────────────────────────────────────
def build_returns(prices: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly returns for each asset, both nominal and inflation-adjusted.

    Nominal return: simple % change in price month-over-month.
    Real return: nominal return minus monthly inflation rate.
        real_r ≈ nominal_r - inflation_monthly
        (exact: (1 + nominal) / (1 + inflation) - 1)

    Also computes cumulative indexed performance (base = 100 at START_DATE)
    for charting in Power BI.
    """
    # Resample daily prices to month-end
    monthly = prices.resample("MS").last()

    # Nominal monthly returns
    returns = monthly.pct_change() * 100
    returns.columns = [f"{c}_return_pct" for c in returns.columns]

    # Monthly CPI inflation
    macro_aligned = macro["CPI"].reindex(monthly.index, method="ffill")
    inflation_monthly = macro_aligned.pct_change() * 100

    # Real returns
    for asset in TICKERS.keys():
        col = f"{asset}_return_pct"
        returns[f"{asset}_real_return_pct"] = (
            ((1 + returns[col] / 100) / (1 + inflation_monthly / 100) - 1) * 100
        )

    # Cumulative performance index (base 100)
    for asset in TICKERS.keys():
        col = f"{asset}_return_pct"
        returns[f"{asset}_cumulative"] = (
            (1 + returns[col] / 100).cumprod() * 100
        )

    returns.index.name = "date"
    returns.to_csv(F_RETURNS)
    print(f"[OK] {F_RETURNS.name}  ({len(returns)} rows)")
    return returns


# ─────────────────────────────────────────────────────────────────────────────
# 4. Master merge
# ─────────────────────────────────────────────────────────────────────────────
def build_master(prices: pd.DataFrame, macro: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    """
    Merges daily prices, monthly macro, and monthly returns into one
    analysis-ready dataset. Macro and returns are forward-filled to daily
    frequency so everything shares a common date index.
    """
    # Resample macro to daily, forward-fill
    macro_daily = macro.resample("D").last().ffill()
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

    print("\nPreview — master (last 5 rows):")
    cols = ["BTC", "GOLD", "ETF", "CPI_indexed", "inflation_yoy", "FED_FUNDS"]
    print(master.tail(5)[cols].round(2).to_string())