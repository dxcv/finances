import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt
from scipy.interpolate import interp1d
import random
from scipy.stats import norm, t
from finances.market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()

def generate_projected_sample(returns_data, N=30, sample_size=50000, distribution=t):
    np.random.seed(seed=123)
    projected_returns = pd.DataFrame()
    for r in returns_data:
        rets = returns_data[r]        
        # MLE of the sample for a general distribution (to be improved) 
        dist_fit_params = distribution.fit(rets)
        
        projected_sample = np.zeros(sample_size)
        for k in range(N):
            projected_sample += distribution.rvs(*dist_fit_params, size=sample_size)
        #add that as new returns for the month
        projected_returns[r] = projected_sample
    return projected_returns

def generate_shuffled_projected_sample(returns_data, N=30):
    seed=123
    projected_returns = pd.DataFrame()
    for r in returns_data:
        rets = returns_data[r].values
        
        projected_sample = np.zeros(len(rets))
        for k in range(N):
            random.Random(seed).shuffle(rets)
            projected_sample += rets
        
        #add that as new returns for the month
        projected_returns[r] = projected_sample

    return projected_returns


def generate_projected_normal_sample(returns_data, N=30, sample_size=5000):
    np.random.seed(seed=123)
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

def market_tangent_point(returns_data):
    avg_rets = returns_data.mean()
    cov_mat = returns_data.cov()

    # calculate the Markowitz optimal allocations for each target return value
    optimal_weights = pfopt.tangency_portfolio(cov_mat=cov_mat, exp_rets=avg_rets)

    matrix_rets = avg_rets.as_matrix()
    matrix_cov = cov_mat.as_matrix()
    reward = optimal_weights.dot(matrix_rets)
    risk = np.sqrt(optimal_weights.dot(matrix_cov.dot(optimal_weights)))

    return reward, risk


def return_from_risk(returns_data, N):
    projected_returns = generate_projected_sample(returns_data, N)
    rewards, risks = markowitz_efficient_frontier(projected_returns)

    risk_function = interp1d(risks, rewards)
    return risk_function


if __name__=='__main__':

    returns_data = mkt.crypto_returns_data(
        symbols= ['BTC', 'ETH', 'LTC', 'XRP', 'DASH', 'XMR', 'IOTA', 'ADA', 'XLM', 'TRX', 'BCH', 'FUN', 'EMC2', 'UBQ', 'BIS', 'ADST', 'NEO', 'NEM']
        ).dropna()

    import seaborn as sns
    sns.set()
    sns.set_palette('YlOrRd', 12)
    for days in [14]:#range(1,30, 5):
        monthly_returns = generate_projected_normal_sample(returns_data, days)
        rewards, risks = markowitz_efficient_frontier(monthly_returns)
        plt.plot(risks, rewards, label='%i days' % days)
        sharpe = market_tangent_point(monthly_returns)
        print(sharpe[1], sharpe[0])
        plt.plot(sharpe[1], sharpe[0], 'ko')
    plt.legend()
    
    plt.show()

    sns.set()
    f = norm.pdf(np.arange(-1.0, 1.50, 0.001), 0.25, 0.125)
    plt.plot(np.arange(-1.0, 1.50, 0.001), f)
    plt.show()