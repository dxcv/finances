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

# sns.set_style('whitegrid')
# sns.set_context('talk')
# sns.set_palette('dark')

# os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

# # # # Load data from statsmodels datasets
# start = datetime(2014, 9, 1)
# end = datetime(2018, 9, 1)
# df = web.DataReader([
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
# 'PG',
# 'INTC',
# 'PFE',
# 'VZ',
# 'CVX',
# 'UNH',
# 'CSCO',
# 'T',
# 'MRK',
# 'WFC',
# 'HD',
# 'MA',
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
# 'BMY',
# 'LOW',
# 'BKNG',
# 'DHR',
# 'CAT',
# 'USB',
# 'AXP',
# 'ANTM',
# 'COP',
# 'UPS',
# 'LMT',
# 'CVS',
# 'MDLZ',
#     ], 'tiingo', start, end)
# df['logP'] = np.log(df['close'])
# df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
# df.to_csv('data_test_medium.csv')

# print(df)

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

# now calculate the shrinked mean
T = len(df)
gamma = mean_gamma(m, matrix_cov, T)
b = mean_b(m, matrix_cov)
print(gamma)
print(m)
print(b)
stocks.set_estimated_mu_cumm_rets((1-gamma)*m+gamma*b)


mean_hori, cov_hori = stocks.stats_linear_rets_at_horizon()


print(mean_hori)
print(cov_hori)

from pypfopt.efficient_frontier import EfficientFrontier


ef = EfficientFrontier(mean_hori, cov_hori)
weights = ef.efficient_return(0.20)
cleaned_weights = ef.clean_weights()
print(cleaned_weights)
ef.portfolio_performance(verbose=True)


from pypfopt import discrete_allocation
allocation, leftover = discrete_allocation.portfolio(
    weights, stocks.latest_prices, total_portfolio_value=5000
)

print(allocation)
print("Funds remaining: ${:.2f}".format(leftover))