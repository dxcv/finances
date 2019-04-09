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

# os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

# # # # Load data from statsmodels datasets
# start = datetime(2014, 4, 1)
# end = datetime(2018, 10, 1)
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
# # 'DWDP',
# 'IBM',
# 'MDT',
# 'UNP',
# 'CRM',
# 'MMM',
# 'ABBV',
# 'AMGN',
# 'LLY',
# # 'PYPL',
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
# # 'LIN',
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

# print(df.head(10))

# df.to_csv('data_test_full.csv')

df = pd.read_csv('data_test_full.csv', index_col=['symbol', 'date'])

# df = df.iloc[df.index.get_level_values('date') < '2018-04-01']

stocks = AssetsData(stock_data=df, N_horizon=126)
from sklearn import covariance

print(stocks.cumm_returns.tail(5))
print(stocks.cumm_returns.columns[stocks.cumm_returns.isna().any()].tolist())

# set estimated covariance
matrix_cov = covariance.ledoit_wolf(stocks.cumm_returns)[0]
stocks.set_estimated_cov_cumm_rets(matrix_cov)


# now calculate the shrinked mean
m = stocks.cumm_returns.mean()

T = len(df)
gamma = mean_gamma(m, matrix_cov, T)
b = mean_b(m, matrix_cov)
stocks.set_estimated_mu_cumm_rets(m*(1-gamma)+gamma*b)


mean_hori, cov_hori = stocks.stats_at_horizon(data='linear')
# print(stocks.stats_at_horizon(data='cumm'))
# print(stocks.stats_at_horizon(data='prices'))
# print(stocks.stats_at_horizon(data='linear'))


from finances.investment.tools.efficient_frontier import EfficientFrontier


ef = EfficientFrontier(mean_hori, cov_hori)

MV = ef.create_mv_frontier(500)

# print some weigths performance
desired_return = 0.77

idx = ef.efficient_frontier[ef.efficient_frontier['expected_returns']<desired_return].index[-1]
weights_mv = ef.efficient_frontier[ef.tickers]
ww = weights_mv.loc[idx]
print(ww)

Ret = np.dot(ww, ef.expected_returns)
Vol = np.sqrt(np.dot(ww,np.dot(ef.cov_matrix, ww)))

ef.efficient_return(desired_return)
w_10 = ef.clean_weights()
w_10_clean = pd.Series({i: w_10[i] for i in w_10 if w_10[i] > 0})

print(w_10_clean)

from pypfopt import discrete_allocation
allocation, leftover = discrete_allocation.portfolio(
    w_10, stocks.latest_prices, total_portfolio_value=3000
)
print(allocation)

# plot
ef.plot_mv_frontier()

ax = ef.plot_scatter_efficient(10000)

ax.plot(Vol, Ret, 'bo')

# plt.show()

##############

def convert_to_no(x):
    allocation, leftover = discrete_allocation.portfolio(
        x.to_dict(), stocks.latest_prices, total_portfolio_value=2000
    )
    return pd.Series(allocation)

portfolio_assets_number_df = weights_mv.apply(convert_to_no, axis=1)
portfolio_assets_number_df = portfolio_assets_number_df.fillna(0)


monte_carlo_samples = stocks.draw_random_prices_at_horizon(10000)

gamma_obj = -10.0

def objective(weigths, prices):
    return (np.sum(weigths*prices))**(gamma_obj)/gamma_obj

monte_carlo = ef.efficient_frontier[['volatility']]
for n, p in enumerate(monte_carlo_samples):
    # value = weights_mv.dot(p)
    value = portfolio_assets_number_df.apply(lambda x: objective(x, p), axis=1)
    monte_carlo['sample_'+str(n+1)] = value

fig, ax = plt.subplots(1,1)
# monte_carlo = monte_carlo.set_index('volatility')
M = (gamma_obj*monte_carlo.drop('volatility', axis=1).mean(axis=1))**(1.0/gamma_obj)
M.plot(ax=ax, style='k')
# monte_carlo.min(axis=1).plot(ax=ax, style='--r')
# monte_carlo.mean(axis=1).plot(ax=ax, style='--b')
# plt.plot(ef.efficient_frontier['volatility'], value, 'o')
print(M)
print(M.idxmax())
optimal = portfolio_assets_number_df.loc[M.idxmax()]
print(optimal[optimal>0])
plt.show()

