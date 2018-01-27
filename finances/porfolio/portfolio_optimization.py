import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt

from market import market_data as mkt_data

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()
returns = mkt.crypto_returns_history(symbols=['BTC', 'ETH', 'XRP', 'XLM', 'ADA', 'TRX', 'ADST']).dropna()

avg_rets = returns.mean()
cov_mat = returns.cov()

print(avg_rets)

a= avg_rets.quantile(0.5)

weights = pfopt.markowitz_portfolio(cov_mat=cov_mat, exp_rets=avg_rets, target_ret=a)

print(weights)
print(weights.values)
