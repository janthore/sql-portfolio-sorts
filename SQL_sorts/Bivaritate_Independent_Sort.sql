-- CTE to compute both portfolios market cap and momentum simutaniously independent
WITH bivariate_portfolios_independent AS (
    SELECT
        ticker,
        date,
        market_cap,   
        NTILE(3) OVER (
            PARTITION BY date
            ORDER BY market_cap
            ) AS portfolio_market_cap,
        NTILE(3) OVER (
            PARTITION BY date
            ORDER BY momentum
            ) AS portfolio_momentum,
        LEAD(return, 1) OVER (PARTITION BY ticker ORDER BY date) AS return_t_1
    FROM sp500_market_cap
    LEFT JOIN sp500_returns USING (date, ticker)
    LEFT JOIN sp500_momentum USING (date, ticker)
    WHERE market_cap IS NOT NULL AND return IS NOT NULL AND date >= '2020-01-01'
)

/*
Value Weighted Return with Independent Bivariate Sort on Market Cap and Momentum
    - Portfolios are formed in time t using market_cap_t and momentum_t
    - Returns are calculated in time t+1
    - The portfolios are rebalanced every month
*/

-- 
SELECT portfolio_market_cap, portfolio_momentum, 
    SUM(LN(1 + portfolio_return)) AS cum_log_return 
FROM(
    SELECT portfolio_market_cap, portfolio_momentum,
        date,
        SUM(market_cap * return_t_1) / SUM(market_cap) AS portfolio_return
        FROM bivariate_portfolios_independent
        GROUP BY portfolio_market_cap, portfolio_momentum, date
        ORDER BY portfolio_market_cap, portfolio_momentum DESC, date ASC
) AS independent_portfolios
GROUP BY portfolio_market_cap, portfolio_momentum