import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from finances.investment.tools.assets_data import AssetsData

def estimator_mean(x):
    return np.mean(x)

def estimator_mean_exp(x):
    T = len(x)
    t = np.arange(T)+1.0
    w = (1-0.01)**(T-t)
    return np.sum(w*x)/np.sum(w)


def difference_mean_estimation(df, t_horizon, t_estimation, estimator=np.mean):
    fom_list = []
    fom_df = pd.DataFrame()
    estimation_df = df.rolling(t_estimation).apply(estimator).dropna()

    horizon_df = df.iloc[::-1].rolling(t_horizon).mean().iloc[::-1]

    #
    diff_df = abs(estimation_df-horizon_df).dropna()*100

    return diff_df


###################

data = pd.read_csv('data_test_verysmall.csv', index_col=['symbol', 'date'])

assets = AssetsData(stock_data=data)
df = assets.cumm_returns
df.head()
df.index = pd.to_datetime(df.index)

fom_df = pd.DataFrame()

estimation_range = np.arange(50,1000,25)
for t_estimation in estimation_range:
    diff_df = difference_mean_estimation(df, 252, t_estimation)
    if len(diff_df)<100:
        break
    fom_df[t_estimation] = diff_df.mean()

fom_df=fom_df.T

ax = fom_df.plot(style='-o', subplots=True, layout=(5,3), figsize=(15,15))


fom_df = pd.DataFrame()
estimation_range = np.arange(50,1000,25)
for t_estimation in estimation_range:
    diff_df = difference_mean_estimation(df, 252, t_estimation, estimator=estimator_mean_exp)
    if len(diff_df)<100:
        break
    fom_df[t_estimation] = diff_df.mean()

fom_df=fom_df.T
fom_df.plot(style='-o', subplots=True, layout=(5,3), figsize=(15,15), ax=ax.ravel())
plt.show()
