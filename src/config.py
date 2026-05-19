"""
config.py
---------
Central path and project configuration.
All other scripts import from here — never hardcode paths elsewhere.

FRED API key is loaded from .env file (never hardcoded).
Create a .env file in the project root with:
    FRED_API_KEY=your_key_here
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Project root ──────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# ── Load .env ─────────────────────────────────────────────────────────────────
load_dotenv(ROOT / ".env")
FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise EnvironmentError("FRED_API_KEY not set. Add it to your .env file in the project root.")

# ── Output filenames ──────────────────────────────────────────────────────────
F_PRICES  = PROCESSED / "prices_daily.csv"    # all assets — trading days only, USD
F_MACRO   = PROCESSED / "macro_monthly.csv"   # CPI, Fed Funds Rate — monthly
F_RETURNS = PROCESSED / "returns.csv"         # monthly returns, nominal + real
F_MASTER  = PROCESSED / "master.csv"          # all merged, analysis-ready

# ── Assets (Yahoo Finance tickers) ───────────────────────────────────────────
TICKERS = {
    "BTC":  "BTC-USD",
    "GOLD": "GLD",
    "ETF":  "ACWI",
}

# ── FRED series IDs ───────────────────────────────────────────────────────────
FRED_SERIES = {
    "CPI":       "CPIAUCSL",   # US CPI All Urban Consumers (monthly)
    "FED_FUNDS": "FEDFUNDS",   # Effective Federal Funds Rate (monthly)
}

# ── Analysis period ───────────────────────────────────────────────────────────
# BTC data from ~2014. GLD and ACWI have data before that.
# Common start is determined by the inner join across BTC, GOLD, ETF.
START_DATE = "2014-01-01"
END_DATE   = "2026-05-01"

# ── Sanity check ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"ROOT      : {ROOT}")
    print(f"RAW       : {RAW}")
    print(f"PROCESSED : {PROCESSED}")
    print(f"Tickers   : {list(TICKERS.values())}")
    print(f"Period    : {START_DATE} → {END_DATE}")
    print(f"FRED Key  : OK")