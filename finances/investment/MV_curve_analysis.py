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


    # # print(cov_mat.values)
    # GG = np.vstack(
    #         (-exp_vect.values,
    #         -np.identity(n),
    #         # current_prices.values
    #         ))
    # print(GG)

    # exit(0)

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

import seaborn as sns

np.random.seed(seed=233423)

sns.set_style('whitegrid')
sns.set_context('talk')


from finances.investment.multivariate_estimation import shrinked_estimate_multivariate
os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

N_DAYS = 15

# Load data from statsmodels datasets
start = datetime(2014, 9, 1)
end = datetime(2019, 9, 1)
SPY_holdings= [
'VOO',
'VWOB',
'MSFT',
'AAPL',
'AMZN',
'FB',
'JNJ',
'GOOG',
'GOOGL',
'JPM',
'XOM',
# 'V',
# 'BAC',
'PG',
'INTC',
'PFE',
'VZ',
'CVX',
'UNH',
'CSCO',
'T',
'MRK',
'WFC',
'HD',
'MA',
'BA',
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
## 'ADBE',
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
# 'AMT',
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
# 'GS',
# 'BDX',
# 'QCOM',
# 'ADP',
# 'INTU',
# 'TJX',
# 'DUK',
# 'BIIB',
# 'ISRG',
# 'CB',
# 'CI',
# 'CME',
# 'CHTR',
# 'CELG',
# 'PNC',
# 'SYK',
# 'SLB',
# 'CSX',
# 'D',
# 'CL',
# 'BSX',
# 'MS',
# 'SPG'
]
df = web.DataReader(SPY_holdings, 'tiingo', start, end)
df['logP'] = np.log(df['close'])
df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
df.to_csv('SPY_data.csv')


list_N = np.arange(3, 16, 2)
sns.set_palette('Blues', len(list_N))

for n in list_N:
    data = df['cum_rets'].unstack('symbol')[SPY_holdings[:n]].dropna()

    print(n)

    shrinked_mean, shrinked_cov = shrinked_estimate_multivariate(data)

    current_prices = df['close'].unstack('symbol').dropna()[SPY_holdings[:n]].iloc[-1]


    exp_hor, cov_hori = prices_at_horizon(current_prices,mean=shrinked_mean,cov=shrinked_cov,n_periods=120)


    expt_list = []
    std_list = []
    budget = 1000.0
    maximum_expt=max((exp_hor/current_prices).values*budget)
    print(maximum_expt)
    for e in np.arange(1000,maximum_expt,10):
        try:
            print(e)
            alpha = get_optimized_allocation(
                cov_mat=cov_hori,
                exp_vect=exp_hor,
                target_mean=e,
                budget=budget,
                current_prices=current_prices)
        except ValueError:
            print('ERROR', e)
            break


        expected_val = np.sum(alpha.values*exp_hor)

        a1,a2 = np.meshgrid(alpha, alpha)
        std = np.sqrt(np.sum(np.sum(a1*cov_hori*a2)))

        expt_list.append(expected_val)
        std_list.append(std)

    print(alpha)


    plt.plot(std_list, expt_list, '-o', label=n)
plt.legend()
plt.show()