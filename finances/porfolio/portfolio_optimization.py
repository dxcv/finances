import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt

from scipy.stats import norm
from market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()
returns = mkt.crypto_returns_history(symbols=['ADA', 'ADST', 'BTC', 'BIS', 'NEO', 'EMC2', 'ETH', 'FUN', 'IOTA', 'LTC', 'TRX', 'UBQ', 'XLM', 'XRP']).dropna()

print(returns)
month_returns = pd.DataFrame()

# for r in returns.columns:
#     print(r)
#     rets = returns[r]
#     kde = sm.nonparametric.KDEUnivariate(rets)
#     kde.fit()
#     ret_value = kde.support
#     pdf = kde.density
#     prob = pdf*(ret_value[-1]-ret_value[0])/(len(pdf)-1)
#     prob[prob < 0] = 0
#     sample = np.random.choice(ret_value, p=prob, size=100000)
#     for k in range(1):
#         sample += np.random.choice(ret_value, p=prob, size=100000)
#     month_returns[r] = sample

n_days = 30

# calculate monthly distribution
for r in returns.columns:
    rets = returns[r]
    daily_mu, daily_std = norm.fit(rets)
    monthly_mu, monthly_std = n_days*daily_mu, daily_std*np.sqrt(n_days)
    monthly_data = norm.rvs(monthly_mu, monthly_std, size=1000)
    month_returns[r] = monthly_data


returns = month_returns
print(returns)

avg_rets = returns.mean()
cov_mat = returns.cov()

print(cov_mat)

tgt_return = avg_rets.quantile(0.6)

print(tgt_return)

weights_optimal = pfopt.markowitz_portfolio(cov_mat=cov_mat, exp_rets=avg_rets, target_ret=tgt_return)
weights_optimal = pfopt.truncate_weights(weights_optimal)

print(weights_optimal)

weights_sharpe = pfopt.tangency_portfolio(cov_mat=cov_mat, exp_rets=avg_rets)
weights_sharpe = pfopt.truncate_weights(weights_sharpe)

print(weights_sharpe)