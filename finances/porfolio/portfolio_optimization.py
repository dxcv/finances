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
returns = mkt.crypto_returns_history(
    symbols=['ADA', 'XMR', 'ADST', 'BTC', 'BIS', 'NEO', 'EMC2', 'ETH', 'FUN', 'IOTA', 'LTC', 'TRX', 'UBQ', 'XLM', 'XRP']
    ).dropna()

def generate_projected_normal_sample(returns_data, N=30, sample_size=1000):
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
    # return optimal_allocation



if __name__=='__main__':

    reward = return_from_risk(returns, 60)
    print(reward(0.22))
    import seaborn as sns
    sns.set()
    sns.set_palette('YlOrRd', 12)
    for days in range(1,60, 5):
        monthly_returns = generate_projected_normal_sample(returns, days)
        rewards, risks = markowitz_efficient_frontier(monthly_returns)
        plt.plot(risks, rewards, label='%i days' % days)
    plt.legend()
    plt.show()

    print(optimal_allocation(returns, 0.2, 30))