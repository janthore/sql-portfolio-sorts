# Portfolio Sorts in SQL

This project is a small side project exploring how portfolio sorts can be implemented directly with SQL queries.  
The repository contains implementations of the following portfolio constructions:

- [Univariate Equally Weighted](SQL_sorts/Univariate_Sort_Equally_Weighted.sql)
- [Univariate Value Weighted](SQL_sorts/Univariate_Sort_Value_Weighted.sql)
- [Bivariate Independent Sort](SQL_sorts/Bivaritate_Independent_Sort.sql)
- [Bivariate Dependent Sort](SQL_sorts/Bivariate_Dependent_Sort.sql)

The data used in this project comes from **public data accessed via yfinance**.  
The script that fetches and prepares the data can be found [here](data_generation/build_dataset.py).

For the portfolio formation I computed several firm characteristics that are commonly used in asset pricing research:

- **Momentum**
- **Market Capitalization**
- **Volatility**
- **Historic Beta**

It is important to note that the dataset only contains companies that are part of the **S&P 500 as of Q1 2026**.  
As a consequence, the results are affected by **survivorship bias**, since firms that left the index historically are not included.

Using the queries in this repository it is possible to compute portfolio returns for different sorting schemes.  
For example, the following figure shows the performance of portfolios sorted jointly on **market capitalization and momentum**:

<img width="640" height="480" alt="market_cap_x_momentum" src="https://github.com/user-attachments/assets/c4f1e6da-01e6-40b1-8e14-a091587b2f90" />

A first inspection suggests that the portfolio consisting of **small-cap stocks with high momentum** exhibits the strongest historical performance within the sample.  
However, this result should be interpreted cautiously, as the restricted universe of surviving S&P 500 firms can strongly influence the observed return patterns.
