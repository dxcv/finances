import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

from finances.investment.assets_data import AssetsData
from scipy.optimize import minimize

pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'



# # # # Load data from statsmodels datasets
# start = datetime(2016, 4, 1)
# end = datetime(2019, 4, 1)
# df = web.DataReader([
# 'VXUS',
# 'VTI',
# 'MSFT',
# 'AAPL',
# 'AMZN',
# 'VOO',
#     ], 'tiingo', start, end)
# df['logP'] = np.log(df['close'])
# # df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
# df.to_csv('data_test.csv')

df = pd.read_csv('data_test.csv', index_col=['symbol', 'date'])

stock_data = AssetsData(stock_data=df, N_horizon=126)

from sklearn import covariance

matrix_cov = stock_data.cumm_returns.cov()

stock_data.set_estimated_cov_cumm_rets(
    pd.DataFrame(
        matrix_cov,
        index=stock_data.assets,
        columns=stock_data.assets)
)

n_assets = len(stock_data.assets)

# now calculate the shrinked mean
m = stock_data.cumm_returns.mean()

# now calculate the shrinked mean
T = len(df)
stock_data.set_estimated_mu_cumm_rets(m)


mean_hori, cov_hori = m*252, matrix_cov*252  #stock_data.stats_linear_rets_at_horizon()

np.random.seed(42)
num_ports = 100
all_weights = np.zeros((num_ports, n_assets))
ret_arr = np.zeros(num_ports)
vol_arr = np.zeros(num_ports)
sharpe_arr = np.zeros(num_ports)

for x in range(num_ports):
    # Weights
    weights = np.array(np.random.random(n_assets))
    weights = weights/np.sum(weights)
    
    # Save weights
    all_weights[x,:] = weights
    
    # Expected return
    ret_arr[x] = np.sum( (mean_hori * weights ))
    
    # Expected volatility
    vol_arr[x] = np.sqrt(np.dot(weights.T, np.dot(cov_hori, weights)))
    
    # Sharpe Ratio
    sharpe_arr[x] = ret_arr[x]/vol_arr[x]


plt.figure(figsize=(12,8))
plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Volatility')
plt.ylabel('Return')
# plt.scatter(max_sr_vol, max_sr_ret,c='red', s=50) # red dot
plt.show()


def get_ret_vol_sr(weights):
    weights = np.array(weights)
    ret = np.sum(mean_hori * weights)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_hori, weights)))
    sr = ret/vol
    return np.array([ret, vol, sr])

def neg_sharpe(weights):
# the number 2 is the sharpe ratio index from the get_ret_vol_sr
    return get_ret_vol_sr(weights)[2] * -1

def check_sum(weights):
    #return 0 if sum of the weights is 1
    return np.sum(weights)-1


cons = ({'type': 'eq', 'fun': check_sum})
bounds = []
init_guess = []
for n in range(n_assets):
    bounds.append((0,1))
    init_guess.append(0.25)

frontier_y = np.linspace(0,0.3,50)

def minimize_volatility(weights):
    return get_ret_vol_sr(weights)[1]

frontier_x = []

for possible_return in frontier_y:
    cons = ({'type':'eq', 'fun':check_sum},
            {'type':'eq', 'fun': lambda w: get_ret_vol_sr(w)[0] - possible_return})
    
    result = minimize(minimize_volatility,init_guess, method='SLSQP', bounds=bounds, constraints=cons)
    frontier_x.append(result['fun'])



plt.figure(figsize=(12,8))
plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Volatility')
plt.ylabel('Return')
plt.plot(frontier_x,frontier_y, 'r--', linewidth=3)
plt.show()