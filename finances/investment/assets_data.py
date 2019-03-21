import os
import numpy as np
import pandas as pd

class AssetsData(object):
    stock_data = None
    mu_cumm_rets = None
    cov_cumm_rets = None
    mu_linear_rets = None
    cov_linear_rets = None

    def __init__(self, stock_data, estimation_period=1, N_horizon=120):
        stock_data['logP'] = np.log(stock_data['close'])
        self.stock_data = stock_data
        self.estimation_period = estimation_period
        self.N_horizon = N_horizon

    @property
    def latest_prices(self):
        return self.stock_data['close'].unstack('symbol').dropna().iloc[-1]
    
    @property
    def cumm_returns(self):
        rets_data = self.stock_data['logP'].unstack('symbol').iloc[::self.estimation_period].rolling(2).apply(lambda x: x[-1]-x[0], raw=True)
        self.cumm_returns_data = rets_data.dropna()
        return self.cumm_returns_data

    @property
    def linear_returns(self):
        linear = self.stock_data['close'].unstack('symbol').iloc[::self.estimation_period].rolling(2).apply(lambda x: x[-1]/x[0]-1, raw=True)
        self.linear_returns_data = linear.dropna()
        return self.linear_returns_data

    def stats_horizon_cumm_rets(self):
        mean = self.mu_cumm_rets
        cov = self.cov_cumm_rets
        return mean*self.N_horizon, cov*self.N_horizon

    def stats_horizon_prices(self):
        mean = self.mu_cumm_rets
        cov = self.cov_cumm_rets

        K = np.diagonal(cov)
        mean_hori = self.latest_prices*np.exp(self.N_horizon*(mean + 0.5*K))
        Ln,Lm = np.meshgrid(mean_hori,mean_hori)
        cov_hori = Ln*Lm*(np.exp(self.N_horizon*cov)-1)
        return mean_hori, cov_hori

    def stats_horizon_linear_rets(self):
        mean_prices, cov_prices = self.stats_horizon_prices()
        inv_prices = 1/self.latest_prices
        mean_hori = inv_prices*mean_prices - 1

        inv_prices_n, inv_prices_m = np.meshgrid(inv_prices, inv_prices)
        cov_hori = inv_prices_n*cov_prices*inv_prices_n

        return mean_hori, cov_hori
