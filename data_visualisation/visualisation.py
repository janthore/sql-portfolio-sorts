import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


engine = create_engine("postgresql://postgres:password@localhost:5432/postgres") #TODO: Delete the server entry

with open("SQL_sorts\BIvariate_Depentend_Sort_time_series.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, engine)

df["portfolio"] = ("mark_cap " + df["portfolio_market_cap"].astype(str) + " x " + "mom " + df["portfolio_momentum"].astype(str))
df["log_return"] = np.log1p(df["portfolio_return"])
df = df.sort_values(["portfolio", "date"])

df["cum_log_return"] = df.groupby("portfolio")["log_return"].cumsum()

sns.lineplot(
    data=df,
    x="date",
    y="cum_log_return",
    hue="portfolio",
)
plt.show()