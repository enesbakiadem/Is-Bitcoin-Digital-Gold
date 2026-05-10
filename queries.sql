-- ============================================================
-- Asset Comparison Analysis — SQL Queries
-- ============================================================
-- Open assets.db in DB Browser for SQLite, then run these.
-- All prices in USD. Period: Nov 2017 – Apr 2026.
-- ============================================================


-- ── 1. Best and worst performing asset per year ──────────────
-- Which asset won each year by nominal return?

WITH monthly_first AS (
    SELECT
        strftime('%Y', date) AS year,
        MIN(date)            AS first_date
    FROM returns_monthly
    GROUP BY year
),
monthly_last AS (
    SELECT
        strftime('%Y', date) AS year,
        MAX(date)            AS last_date
    FROM returns_monthly
    GROUP BY year
),
yearly_returns AS (
    SELECT
        strftime('%Y', r.date) AS year,
        'BTC'  AS asset, AVG(r.BTC_return_pct)  AS avg_monthly_return FROM returns_monthly r GROUP BY year
    UNION ALL SELECT strftime('%Y', date), 'ETH',  AVG(ETH_return_pct)  FROM returns_monthly GROUP BY strftime('%Y', date)
    UNION ALL SELECT strftime('%Y', date), 'GOLD', AVG(GOLD_return_pct) FROM returns_monthly GROUP BY strftime('%Y', date)
    UNION ALL SELECT strftime('%Y', date), 'ETF',  AVG(ETF_return_pct)  FROM returns_monthly GROUP BY strftime('%Y', date)
    UNION ALL SELECT strftime('%Y', date), 'EM',   AVG(EM_return_pct)   FROM returns_monthly GROUP BY strftime('%Y', date)
    UNION ALL SELECT strftime('%Y', date), 'BOND', AVG(BOND_return_pct) FROM returns_monthly GROUP BY strftime('%Y', date)
),
ranked AS (
    SELECT
        year,
        asset,
        ROUND(avg_monthly_return * 12, 2) AS est_annual_return_pct,
        RANK() OVER (PARTITION BY year ORDER BY avg_monthly_return DESC) AS rnk
    FROM yearly_returns
)
SELECT year, asset AS winner, est_annual_return_pct
FROM ranked
WHERE rnk = 1
ORDER BY year;


-- ── 2. Months where BTC > 10% and Gold was negative ──────────
-- How often did BTC rally hard while Gold fell?
-- If they were correlated, this should be rare.

SELECT
    date,
    ROUND(BTC_return_pct,  2) AS btc_return,
    ROUND(GOLD_return_pct, 2) AS gold_return
FROM returns_monthly
WHERE BTC_return_pct  >  10
  AND GOLD_return_pct <   0
ORDER BY BTC_return_pct DESC;


-- ── 3. Worst 10 months for each asset ────────────────────────

SELECT 'BTC' AS asset, date, ROUND(BTC_return_pct, 2) AS return_pct
FROM (SELECT date, BTC_return_pct FROM returns_monthly ORDER BY BTC_return_pct ASC LIMIT 10)
UNION ALL
SELECT 'GOLD', date, ROUND(GOLD_return_pct, 2)
FROM (SELECT date, GOLD_return_pct FROM returns_monthly ORDER BY GOLD_return_pct ASC LIMIT 10)
UNION ALL
SELECT 'ETF', date, ROUND(ETF_return_pct, 2)
FROM (SELECT date, ETF_return_pct FROM returns_monthly ORDER BY ETF_return_pct ASC LIMIT 10)
ORDER BY asset, return_pct;


-- ── 4. How many days was each asset below its ATH? ───────────

SELECT
    'BTC'  AS asset, COUNT(*) AS days_below_ath
    FROM drawdown_history WHERE BTC_drawdown_pct  < 0
UNION ALL SELECT 'ETH',  COUNT(*) FROM drawdown_history WHERE ETH_drawdown_pct  < 0
UNION ALL SELECT 'GOLD', COUNT(*) FROM drawdown_history WHERE GOLD_drawdown_pct < 0
UNION ALL SELECT 'ETF',  COUNT(*) FROM drawdown_history WHERE ETF_drawdown_pct  < 0
UNION ALL SELECT 'EM',   COUNT(*) FROM drawdown_history WHERE EM_drawdown_pct   < 0
UNION ALL SELECT 'BOND', COUNT(*) FROM drawdown_history WHERE BOND_drawdown_pct < 0
ORDER BY days_below_ath DESC;


-- ── 5. Simultaneous crash months ─────────────────────────────
-- When did BTC, ETH, and ETF all fall more than 5% in the same month?
-- These are true market panic months.

SELECT
    date,
    ROUND(BTC_return_pct,  2) AS btc,
    ROUND(ETH_return_pct,  2) AS eth,
    ROUND(ETF_return_pct,  2) AS etf,
    ROUND(GOLD_return_pct, 2) AS gold,
    ROUND(BOND_return_pct, 2) AS bond
FROM returns_monthly
WHERE BTC_return_pct < -5
  AND ETH_return_pct < -5
  AND ETF_return_pct < -5
ORDER BY BTC_return_pct ASC;


-- ── 6. Gold vs BOND — safe haven scorecard ───────────────────
-- In months where ETF fell, did Gold or BOND hold up better?
-- Average return of each in negative equity months.

SELECT
    ROUND(AVG(GOLD_return_pct), 2) AS gold_avg_in_bad_equity_months,
    ROUND(AVG(BOND_return_pct), 2) AS bond_avg_in_bad_equity_months,
    COUNT(*)                        AS n_months
FROM returns_monthly
WHERE ETF_return_pct < 0;