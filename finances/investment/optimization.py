import os
import numpy as np
import pandas as pd
import warnings
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import scipy.stats as st
from datetime import datetime
import matplotlib.pyplot as plt

import cvxopt as opt
import cvxopt.solvers as optsolvers

def prices_at_horizon(Pt,mean,cov,n_periods):
    K = np.diagonal(cov)
    E_hori = Pt*np.exp(n_periods*(mean + 0.5*K))
    Ln,Lm = np.meshgrid(E_hori,E_hori)
    Cov_hori = Ln*Lm*(np.exp(n_periods*cov)-1)

    return E_hori, Cov_hori


budget = 1000

def get_optimized_allocation(cov_mat, exp_vect, target_mean, budget, current_prices):

    n = len(cov_mat)

    P = opt.matrix(cov_mat.values)
    q = opt.matrix(0.0, (n, 1))

    # exp_vect*x >= target_mean and x >= 0
    G = opt.matrix(
        np.vstack(
            (-exp_vect.values,
            -np.identity(n),
            current_prices.values
            )
        )
    )
    h = opt.matrix(
        np.vstack(
            (-target_mean,
            np.zeros((n, 1)),
            budget
            )
        )
    )

    # A = opt.matrix(current_prices.values).T
    # b = opt.matrix(budget)


    # Solve
    optsolvers.options['show_progress'] = False
    # sol = optsolvers.qp(P, q, G, h, A, b)
    sol = optsolvers.qp(P, q, G, h)

    if sol['status'] != 'optimal':
        warnings.warn("Convergence problem")

    # Put weights into a labeled series
    alpha = pd.Series(sol['x'], index=cov_mat.index)

    return alpha

def create_efficient_frontier_dataset(exp_hor, cov_hori, current_prices, budget=5000):
    print(current_prices)
    efficient_frontier = pd.DataFrame()
    maximum_expt=max((exp_hor/current_prices).values*budget)
    for m in np.arange(budget,maximum_expt,50):
        try:
            alpha = get_optimized_allocation(
                cov_mat=cov_hori,
                exp_vect=exp_hor,
                target_mean=m,
                budget=budget,
                current_prices=current_prices)
        except ValueError:
            print('ERROR', m)
            break
        efficient_frontier[m] = alpha#*current_prices/sum(alpha*current_prices)
    return efficient_frontier


def calculate_std(x):
    x1,x2 = np.meshgrid(x, x)
    std = np.sqrt(np.sum(np.sum(x1*cov_hori*x2)))
    return std

# def plot_porfolio_distribution(efficient_frontier):


if __name__ == '__main__':
    from finances.investment.multivariate_estimation import shrinked_estimate_multivariate

    import seaborn as sns

    np.random.seed(seed=233423)

    sns.set_style('whitegrid')
    sns.set_context('talk')
    sns.set_palette('dark')

    # os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

    # # Load data from statsmodels datasets
    # start = datetime(2014, 9, 1)
    # end = datetime(2019, 9, 1)
    # df = web.DataReader([
    #     'AMZN','GOOGL','AMT',
    #     'AAPL','MSFT','MMM','VOO',
    #     'ABMD','ABBV','V', 'BA'
    #     ], 'tiingo', start, end)
    # df['logP'] = np.log(df['close'])
    # df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
    # df.to_csv('data_test.csv')


    df = pd.read_csv('data_test.csv', index_col=['symbol', 'date'])

    data = df['cum_rets'].unstack('symbol').dropna()

    shrinked_mean, shrinked_cov = shrinked_estimate_multivariate(data)

    current_prices = df['close'].unstack('symbol').dropna().iloc[-1]

    exp_hor, cov_hori = prices_at_horizon(current_prices,mean=shrinked_mean,cov=shrinked_cov,n_periods=120)

    fig, ax = plt.subplots(2,1, sharex=True)

    frontier = create_efficient_frontier_dataset(exp_hor, cov_hori, current_prices)
    frontier.apply(calculate_std).plot(style='-o', ax=ax[0])
    weigths = frontier.apply(lambda x: x*current_prices/sum(x*current_prices))
    print(weigths)
    a = weigths.rolling(len(weigths), min_periods=1).sum()
    a.transpose().plot(ax=ax[1])
    plt.show()
