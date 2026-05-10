"""
config.py
---------
Central path and project configuration.
All other scripts import from here — never hardcode paths elsewhere.
"""

from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# ── Output filenames ──────────────────────────────────────────────────────────
F_PRICES  = PROCESSED / "prices_daily.csv"    # BTC, Gold, ACWI — daily close USD
F_MACRO   = PROCESSED / "macro_monthly.csv"   # CPI, Fed Funds Rate — monthly
F_RETURNS = PROCESSED / "returns.csv"         # daily/monthly returns, real + nominal
F_MASTER  = PROCESSED / "master.csv"          # all merged, analysis-ready

# ── Assets (Yahoo Finance tickers) ───────────────────────────────────────────
TICKERS = {
    "BTC":  "BTC-USD",   # Bitcoin
    "GOLD": "GLD",       # SPDR Gold Shares ETF (USD, liquid, long history)
    "ETF":  "ACWI",      # iShares MSCI All Country World ETF
}

# ── FRED series IDs ───────────────────────────────────────────────────────────
FRED_SERIES = {
    "CPI":       "CPIAUCSL",   # US CPI All Urban Consumers (monthly)
    "FED_FUNDS": "FEDFUNDS",   # Effective Federal Funds Rate (monthly)
}

# ── Analysis period ───────────────────────────────────────────────────────────
# BTC reliable daily data starts ~2014-09. Everything aligned to this.
START_DATE = "2015-01-01"
END_DATE   = "2026-05-01"

# ── FRED API Key ──────────────────────────────────────────────────────────────
# Get yours at: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "ed0147ac827a51f1a287fc81c10357a7"

# ── Sanity check ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"ROOT      : {ROOT}")
    print(f"RAW       : {RAW}")
    print(f"PROCESSED : {PROCESSED}")
    print(f"Tickers   : {list(TICKERS.values())}")
    print(f"Period    : {START_DATE} → {END_DATE}")
    key_status = "OK" if FRED_API_KEY != "YOUR_KEY_HERE" else "NOT SET"
    print(f"FRED Key  : {key_status}")