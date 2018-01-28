import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt

from market import market_data as mkt_data

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()
returns = mkt.crypto_returns_history(symbols=['BTC', 'ETH', 'XRP', 'XLM', 'ADA', 'TRX', 'ADST', 'BIS', 'IOTA']).dropna()

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