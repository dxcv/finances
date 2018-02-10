import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt
from scipy.interpolate import interp1d

from scipy.stats import norm
from market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()
returns_data = mkt.crypto_returns_data(
    symbols=['ADA', 'XMR', 'ADST', 'BTC', 'BIS', 'NEO', 'EMC2', 'ETH', 'FUN', 'IOTA', 'LTC', 'TRX', 'UBQ', 'XLM', 'XRP', 'DASH']
    ).dropna()

def generate_projected_normal_sample(returns_data, N=30, sample_size=10000):
    projected_returns = pd.DataFrame()
    for r in returns_data:
        rets = returns_data[r]
        
        # MLE of the sample for a normal distribution (to be improved) 
        mu, std = norm.fit(rets)
        projected_mu, projected_std = N*mu, std*np.sqrt(N)

        # generate big sample with the projected distribution
        projected_data = norm.rvs(projected_mu, projected_std, size=sample_size)
        
        #add that as new returns for the month
        projected_returns[r] = projected_data

    return projected_returns

def markowitz_efficient_frontier(returns_data):
    avg_rets = returns_data.mean()
    cov_mat = returns_data.cov()

    # calculate the Markowitz optimal allocations for each target return value
    optimal_allocation_list = []
    for k in np.arange(0.01, 0.99, 0.01):
        tgt_return = avg_rets.quantile(k)
        optimal_weights = pfopt.markowitz_portfolio(cov_mat=cov_mat, exp_rets=avg_rets, target_ret=tgt_return)
        optimal_allocation_list.append(optimal_weights)

    matrix_rets = avg_rets.as_matrix()
    matrix_cov = cov_mat.as_matrix()
    returns = [x.dot(matrix_rets) for x in optimal_allocation_list]
    risks = [np.sqrt(x.dot(matrix_cov.dot(x))) for x in optimal_allocation_list]

    return returns, risks

def return_from_risk(returns_data, N):
    projected_returns = generate_projected_normal_sample(returns_data, N)
    rewards, risks = markowitz_efficient_frontier(projected_returns)

    risk_function = interp1d(risks, rewards)
    return risk_function


if __name__=='__main__':
    n_days = 15

    reward = return_from_risk(returns_data, n_days)
    print(reward(0.11))
    import seaborn as sns
    sns.set()
    # sns.set_palette('YlOrRd', 12)
    for days in [n_days]:#range(1,30, 5):
        monthly_returns = generate_projected_normal_sample(returns_data, days)
        rewards, risks = markowitz_efficient_frontier(monthly_returns)
        plt.plot(risks, rewards, label='%i days' % days)
    plt.legend()


    avg_rets = generate_projected_normal_sample(returns_data, n_days).mean()
    cov_mat = generate_projected_normal_sample(returns_data, n_days).cov()
    x = pfopt.markowitz_portfolio(cov_mat=cov_mat, exp_rets=avg_rets, target_ret=0.2)
    optimal_portfolio = pfopt.truncate_weights(x, min_weight=0.02, rescale=True)
    print(optimal_portfolio)
    # plt.show()

    analysis_df = pd.DataFrame()
    analysis_df['allocation'] = optimal_portfolio
    prices = [get_coin_price(coin) for coin in analysis_df.index]
    # analysis_df.prices =


    