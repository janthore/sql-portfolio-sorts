/*
    - Equal Weighted Univariate Sort on Market Cap
    - Portfolios are formed in time t using market_cap_t
    - Returns are calculated in time t+1
    - The portfolios are rebalanced every month

*/

SELECT
    market_cap_portfolio,
    SUM(LN(1 + portfolio_return)) AS cum_log_return
FROM(
    SELECT
        market_cap_portfolio,
        date,
        AVG(return_t_1) AS portfolio_return
        -- Equal Weighted Return for each portfolio and date
    FROM market_cap_portfolios
    GROUP BY market_cap_portfolio, date
) AS portfolio_returns_equal_weighted
GROUP BY market_cap_portfolio
ORDER BY market_cap_portfolio DESC