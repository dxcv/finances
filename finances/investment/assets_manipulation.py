import os
import numpy as np
import pandas as pd

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

from finances.investment.multivariate_estimation import shrinked_estimate_multivariate, mean_b, mean_gamma

from finances.investment.assets_data import AssetsData


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

df = pd.read_csv('data_test_medium.csv', index_col=['symbol', 'date'])

stocks = AssetsData(stock_data=df, N_horizon=126)
from sklearn import covariance

matrix_cov = covariance.ledoit_wolf(stocks.cumm_returns)[0]

stocks.set_estimated_cov_cumm_rets(
    pd.DataFrame(
        matrix_cov,
        index=stocks.assets,
        columns=stocks.assets)
)

# now calculate the shrinked mean
m = stocks.cumm_returns.mean()

matrix_cov = stocks.cumm_returns.cov()

mean_hori, cov_hori = m, matrix_cov


from finances.investment.efficient_frontier.efficient_frontier import EfficientFrontier


ef = EfficientFrontier(mean_hori, cov_hori)

MV = ef.create_mv_frontier(500)

weights_mv = ef.efficient_frontier[ef.tickers]
ww = weights_mv.iloc[-200]

Ret = np.dot(ww, ef.expected_returns)
Vol = np.sqrt(np.dot(ww,np.dot(ef.cov_matrix, ww)))

print(Vol, Ret)

ef.plot_mv_frontier()

ax = ef.plot_scatter_efficient(10000)

ax.plot(Vol, Ret, 'bo')


plt.show()