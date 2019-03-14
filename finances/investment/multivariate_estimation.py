import os
import numpy as np
import pandas as pd
import warnings
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import scipy.stats as st
from datetime import datetime
import matplotlib.pyplot as plt


def shrinkage_weight(vector,cov):
    c = vector.values[np.newaxis]  # this is the row of the data frame, or c_t
    numerator = np.trace(np.dot(np.dot(c.T,c) - cov,np.dot(c.T,c) - cov)) # this is going to be done to the each line
    denominator = np.trace(np.dot(cov-np.diagonal(cov).mean()*np.eye(len(cov)), cov-np.diagonal(cov).mean()*np.eye(len(cov))))  # this is the denominator of the expression
    return numerator/denominator


def mean_b(mean, cov):
    inv_cov = np.linalg.inv(cov)
    numerator = np.sum(np.dot(inv_cov,mean))
    denominator = np.sum(np.sum(inv_cov))
    return np.ones(len(mean))*numerator/denominator


def mean_gamma(mean, cov, T):
    w, v = np.linalg.eig(cov)
    numerator = len(w)*np.mean(w)-2*np.max(w)
    denominator = np.sum((mean - mean_b(mean, cov))**2)
    return 1/T*numerator/denominator


def shrinked_estimate_multivariate(data):
    """
    It reproduces the steps from page 356 of Meucci's book
        to calculate the shrinkage estimators for the normal distribution.
    """

    # sample estimate the mean and the covariance
    S = data.cov()
    m = data.mean()

    T = len(data)

    def epsilon_per_row(row):
        """
        Calculates the value of epsilon for each row.
        Then, the actual epsilon is the mean of all epsilon_per_row
        """
        return shrinkage_weight(row,S)

    epsilon = 1/T*data.apply(epsilon_per_row, axis=1).mean()

    shrinked_cov = (1-epsilon)*S+epsilon*np.diagonal(S).mean()*np.eye(len(S))

    # now calculate the shrinked mean
    gamma = mean_gamma(m, shrinked_cov, T)
    shrinked_mean = (1-gamma)*m+gamma*mean_b(m, shrinked_cov)

    return shrinked_mean, shrinked_cov


if __name__ == '__main__':
    import seaborn as sns

    np.random.seed(seed=233423)

    sns.set_style('whitegrid')
    sns.set_context('talk')
    sns.set_palette('dark')

    os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

    N_DAYS = 15

    # Load data from statsmodels datasets
    start = datetime(2014, 9, 1)
    end = datetime(2019, 9, 1)
    df = web.DataReader([
        'AMZN','GOOGL','SPY','AMT',
        'AAPL','MSFT','MMM','VOO',
        'ABMD','ABBV','BA'
        ], 'tiingo', start, end)
    df['logP'] = np.log(df['close'])
    df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
    data = df['cum_rets'].unstack('symbol').dropna()

    import time
    start = time.time()
    mean, cov = shrinked_estimate_multivariate(data)


    print(mean, cov)
    print(time.time()-start)