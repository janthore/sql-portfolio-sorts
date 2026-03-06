import numpy as np
import pandas as pd
import requests
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:your_password@localhost:5432/postgres") # Update with your database credentials
start = "2015-01-01"
end = "2026-02-28"


# Fetch the list of S&P 500 companies from Wikipedia
# Node that the wikipedia page only contains the current S&P 500 stocks -> Because of this the analysation contains the survivorship bias !!!
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
response.raise_for_status()

sp500 = pd.read_html(response.text)[0]

tickers = sp500["Symbol"].tolist()
tickers = [t.replace(".", "-") for t in tickers]


# Fetch historical stock price data for the S&P 500 companies and SPY ETF using yfinance
data = yf.download(
    tickers,
    start=start,
    end=end,
    auto_adjust=True
).resample("ME").last()

data_spy = yf.download(
    "SPY",
    start=start,
    end=end,
    auto_adjust=True
).resample("ME").last()


#  Bring Data into SQL natural Form
def sql_form(df, id_name, var_name, value_name):
    try:
        df.index.name = df.index.name.lower()
    except AttributeError:
        pass
    df.columns = df.columns.str.lower()
    return (df.reset_index().melt(id_vars=id_name, var_name=var_name,value_name=value_name ))

# Function to save DataFrame to SQL database
def save_to_db(df, name):
    df.to_sql(name, engine, if_exists="replace", index=False)

# save the tickers to the database
pd_tickers = pd.DataFrame(tickers, columns=["ticker"])
pd_tickers["ticker"] = pd_tickers["ticker"].str.lower()
pd_tickers.to_sql("sp500_tickers", engine, if_exists="replace", index=False)
save_to_db(pd_tickers, "sp500_tickers")


# Compute monthly returns for the S&P 500 companies and SPY ETF
returns = data["Close"].pct_change()
returns_spy = data_spy["Close"].pct_change()
returns_sql = sql_form(returns, "date", "ticker", "return")
returns_spy_sql = sql_form(returns_spy, "date", "ticker", "return")
save_to_db(returns_sql, "sp500_returns")
save_to_db(returns_spy_sql, "spy_returns")

# Save the monthly closing prices for the S&P 500 companies and SPY ETF to the database
prices = data["Close"]
prices_sql = sql_form(prices, "date", "ticker", "price")
save_to_db(prices_sql, "sp500_prices")

# Fetch additional information about the S&P 500 companies using yfinance and save it to the database
# Node that not every information can be used without data leakage
info_data = [] 
for ticker in tickers:
    info = yf.Ticker(ticker).info
    info["ticker"] = ticker
    info_data.append(info)

df_info = pd.DataFrame(info_data)
df_info.set_index("ticker", inplace=True)
bad_cols = [col for col in df_info.columns 
            if df_info[col].apply(lambda x: isinstance(x, (dict, list))).any()]
df_info = df_info.drop(columns=bad_cols)


# Compute and save the momentum factor
momentum = (1 + returns).rolling(11).apply(np.prod) - 1
momentum_sql = sql_form(momentum, "date", "ticker", "momentum")
save_to_db(momentum_sql, "sp500_momentum")


# Compute and save the market capitalization
# market cap_t = price_t * sharesOutstanding <- This is an easy approximation, contains in some cases false data that is not cleaned in this dataset
market_cap = pd.DataFrame(index=data.index, columns=tickers)
for ticker in tickers:
    market_cap[ticker] = data["Close"][ticker] * df_info.loc[ticker, "sharesOutstanding"]
market_cap_sql = sql_form(market_cap, "date", "ticker", "market_cap")
save_to_db(market_cap_sql, "sp500_market_cap")

# Compute and save the historical beta 
betas = pd.DataFrame(index=returns.index, columns=tickers)
for ticker in tickers:
    ticker = ticker.lower()
    cov = returns[ticker].rolling(12).cov(returns_spy["spy"])
    var = returns_spy["spy"].rolling(12).var()
    betas[ticker] = cov / var
betas_sql = sql_form(betas, "date", "ticker", "beta")
save_to_db(betas_sql, "sp500_beta")

# Compute and save the historical volatility
vol = returns.rolling(12).std()
vol_spy = returns_spy.rolling(12).std()


vol_sql = sql_form(vol, "date", "ticker", "volatility")
vol_spy_sql = sql_form(vol_spy, "date", "ticker", "volatility")
save_to_db(vol_sql, "sp500_vol")
save_to_db(vol_spy_sql, "spy_vol")
