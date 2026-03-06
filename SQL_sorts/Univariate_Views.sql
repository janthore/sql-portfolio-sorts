/*
    View to create market cap portfolios based on the S&P 500 data
    - Portfolios are formed in time t using market_cap_t
    - Returns are calculated in time t+1
    - The portfolios are rebalanced every month
*/

DROP VIEW IF EXISTS market_cap_portfolios;
CREATE VIEW market_cap_portfolios AS
    SELECT
        ticker,
        date,
        return_t_1,
        market_cap,
        NTILE(5) OVER (-- Create 5 portfolios based on market cap
            PARTITION BY date
            ORDER BY market_cap
        ) AS market_cap_portfolio
    FROM sp500_market_cap
    LEFT JOIN (
        SELECT
            ticker,
            date,
            LEAD(return, 1) OVER (PARTITION BY ticker ORDER BY date) AS return_t_1
        FROM sp500_returns) AS returns_t_1
    USING (date, ticker)
    WHERE market_cap IS NOT NULL AND return_t_1 IS NOT NULL 
    AND date >= '2020-01-01';