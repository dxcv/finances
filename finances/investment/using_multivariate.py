import os
import numpy as np
import pandas as pd
import warnings
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import scipy.stats as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(seed=233423)

sns.set_style('whitegrid')
sns.set_context('talk')
sns.set_palette('dark')

def shrinkage_weight(vector,covariant):
    c = vector.values[np.newaxis]  # this is the row of the data frame, or c_t
    numerator = np.trace((np.dot(c.T,c) - covariant)**2)  # this is going to be done to the each line
    denominator = np.trace((S-np.diagonal(S).mean()*np.eye(len(S)))**2)  # this is the denominator of the expression
    return numerator/denominator


os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

N_DAYS = 15

# Load data from statsmodels datasets
start = datetime(2014, 9, 1)
end = datetime(2019, 9, 1)
df = web.DataReader(['AMZN','GOOGL','SPY','AMT','AAPL','MSFT'], 'tiingo', start, end)
df['logP'] = np.log(df['close'])
df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
data = df['cum_rets'].unstack('symbol').dropna()

# print(data)
S = data.cov()
m = data.mean()

print(S)

x = data.iloc[0]

def apply_to_dataframe(row):
    return shrinkage_weight(row,S)


eps = 1/len(data)*data.apply(apply_to_dataframe, axis=1).mean()

M = np.diagonal(S).mean()*np.eye(len(S))

Covariant_shrinked = M*eps+(1-eps)*S

print()
