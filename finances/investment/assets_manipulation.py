import os
import numpy as np
import pandas as pd

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

from finances.investment.multivariate_estimation import shrinked_estimate_multivariate, mean_b, mean_gamma

from finances.investment.tools.assets_data import AssetsData


import seaborn as sns

np.random.seed(seed=233423)

sns.set_style('whitegrid')
sns.set_context('talk')
sns.set_palette('dark')

os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

# # # # Load data from statsmodels datasets
# start = datetime(2005, 4, 1)
# end = datetime(2019, 4, 1)
# df = web.DataReader([
# 'VXUS',
# 'VTI',
# 'MSFT',
# 'AAPL',
# 'AMZN',
# 'VOO',
# 'AMT',
# 'GOOGL',
# 'FB',
# 'JNJ',
# 'GOOG',
# 'JPM',
# 'XOM',
# 'V',
# 'BAC',
# # 'PG',
# # 'INTC',
# # 'PFE',
# # 'VZ',
# # 'CVX',
# # 'UNH',
# # 'CSCO',
# # 'T',
# # 'MRK',
# # 'WFC',
# # 'HD',
# # 'MA',
# # 'BA',
# # 'CMCSA',
# # 'KO',
# # 'DIS',
# # 'PEP',
# # 'NFLX',
# # 'C',
# # 'WMT',
# # 'MCD',
# # 'PM',
# # 'ABT',
# # 'ORCL',
# # 'ADBE',
# # 'DWDP',
# # 'IBM',
# # 'MDT',
# # 'UNP',
# # 'CRM',
# # 'MMM',
# # 'ABBV',
# # 'AMGN',
# # 'LLY',
# # 'PYPL',
# # 'HON',
# # 'AVGO',
# # 'NKE',
# # 'ACN',
# # 'MO',
# # 'TMO',
# # 'TXN',
# # 'COST',
# # 'UTX',
# # 'NVDA',
# # 'LIN',
# # 'NEE',
# # 'SBUX',
# # 'GE',
# # 'GILD',
# # 'BMY',
# # 'LOW',
# # 'BKNG',
# # 'DHR',
# # 'CAT',
# # 'USB',
# # 'AXP',
# # 'ANTM',
# # 'COP',
# # 'UPS',
# # 'LMT',
# # 'CVS',
# # 'MDLZ',
#     ], 'tiingo', start, end)
# df['logP'] = np.log(df['close'])

# # df.to_csv('data_test_full.csv')

df = pd.read_csv('data_test_full.csv', index_col=['symbol', 'date'])

stocks = AssetsData(stock_data=df, N_horizon=126)
from sklearn import covariance


# set estimated covariance
matrix_cov = covariance.ledoit_wolf(stocks.cumm_returns)[0]
stocks.set_estimated_cov_cumm_rets(stocks.cumm_returns.cov())


# now calculate the shrinked mean
m = stocks.cumm_returns.mean()

T = len(df)
gamma = mean_gamma(m, matrix_cov, T)
b = mean_b(m, matrix_cov)
stocks.set_estimated_mu_cumm_rets(m)


mean_hori, cov_hori = stocks.stats_at_horizon(data='linear')
# print(stocks.stats_at_horizon(data='cumm'))
# print(stocks.stats_at_horizon(data='prices'))
# print(stocks.stats_at_horizon(data='linear'))

from finances.investment.tools.efficient_frontier import EfficientFrontier


ef = EfficientFrontier(mean_hori, cov_hori)

MV = ef.create_mv_frontier(500)

# print some weigths performance
weights_mv = ef.efficient_frontier[ef.tickers]
ww = weights_mv.iloc[-200]

Ret = np.dot(ww, ef.expected_returns)
Vol = np.sqrt(np.dot(ww,np.dot(ef.cov_matrix, ww)))

ef.efficient_return(0.3)
w_10 = ef.clean_weights()
w_10_clean = {i: w_10[i] for i in w_10 if w_10[i] > 0}
print(w_10_clean)

from pypfopt import discrete_allocation
allocation, leftover = discrete_allocation.portfolio(
    w_10, stocks.latest_prices, total_portfolio_value=2000
)
print(allocation)

# plot
ef.plot_mv_frontier()

ax = ef.plot_scatter_efficient(10000)

ax.plot(Vol, Ret, 'bo')


plt.show()