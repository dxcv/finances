import os
import numpy as np
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

from finances.investment.multivariate_estimation import shrinked_estimate_multivariate

from finances.investment.assets_data import AssetsData
import seaborn as sns

np.random.seed(seed=233423)

# sns.set_style('whitegrid')
# sns.set_context('talk')
# sns.set_palette('dark')

os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

# # Load data from statsmodels datasets
start = datetime(2014, 9, 1)
end = datetime(2019, 9, 1)
df = web.DataReader([
'MSFT',
'AAPL',
'AMZN',
'FB',
'JNJ',
'GOOG',
'GOOGL',
'JPM',
'XOM',
'V',
'BAC',
'PG',
'INTC',
'PFE',
'VZ',
'CVX',
'UNH',
'CSCO',
'VOO',
'T',
'MRK',
'WFC',
'HD',
'MA',
# 'BA',
# 'CMCSA',
# 'KO',
# 'DIS',
# 'PEP',
# 'NFLX',
# 'C',
# 'WMT',
# 'MCD',
# 'PM',
# 'ABT',
# 'ORCL',
# 'ADBE',
# 'DWDP',
# 'IBM',
# 'MDT',
# 'UNP',
# 'CRM',
# 'MMM',
# 'ABBV',
# 'AMGN',
# 'LLY',
# 'PYPL',
# 'HON',
# 'AVGO',
# 'NKE',
# 'ACN',
# 'MO',
# 'TMO',
# 'TXN',
# 'COST',
# 'UTX',
# 'NVDA',
# 'LIN',
# 'NEE',
# 'SBUX',
# 'GE',
# 'GILD',
'BMY',
'AMT',
'LOW',
'BKNG',
'DHR',
'CAT',
'USB',
'AXP',
'ANTM',
'COP',
'UPS',
'LMT',
'CVS',
'MDLZ',
    ], 'tiingo', start, end)
df['logP'] = np.log(df['close'])
df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
df.to_csv('data_test2.csv')


df = pd.read_csv('data_test2.csv', index_col=['symbol', 'date'])

stocks = AssetsData(stock_data=df, N_horizon=126)

stocks.mu_cumm_rets, stocks.cov_cumm_rets = shrinked_estimate_multivariate(stocks.cumm_returns)


mean_hori, cov_hori = stocks.stats_horizon_cumm_rets()

print(mean_hori)
print(cov_hori)

from pypfopt.efficient_frontier import EfficientFrontier

ef = EfficientFrontier(mean_hori, cov_hori)
weights = ef.efficient_return(0.2)
cleaned_weights = ef.clean_weights()
print(cleaned_weights)
ef.portfolio_performance(verbose=True)


from pypfopt import discrete_allocation
allocation, leftover = discrete_allocation.portfolio(
    weights, stocks.latest_prices, total_portfolio_value=5000
)

print(allocation)
print("Funds remaining: ${:.2f}".format(leftover))