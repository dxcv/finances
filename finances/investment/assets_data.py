import os
import numpy as np
import pandas as pd

class AssetsData(object):
    """
    Class that processes the data from the stock market and gets the relevant statistical quantities
        for portfolio optimization.

    Attributes:
        stock_data (DataFrame): pandas Dataframe containing at least a column "close" and with a multiindex
            ['symbol', 'time']
        estimation_period (float): time over which the properties of the stock market are estimated (defaults to 1 day)
        N_horizon (float): the number of "estimation_period"s is the investment horizon (defaults to 120 days)
        assets (float): the list of assets considered (taken from the stock_data dataframe)
        mu_cumm_rets (Series): the estimated mean of the estimation period (index are the "assets")
        cov_cumm_rets (Dataframe): the estimated covariance matrix of the estimation period (columns and index are the "assets")
        mu_linear_rets (Series): the estimated mean of the estimation period (index are the "assets")
        cov_linear_rets (Dataframe): the estimated covariance matrix of the estimation period (columns and index are the "assets")
        latest_prices (Series): the latest prices of the "assets" present in the "stock_data"

    """
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
        self.assets = stock_data.index.get_level_values('symbol').unique()

    @property
    def latest_prices(self):
        """
        Returns the latest values of the 'close' prices within the stock_data dataframe.
        """
        return self.stock_data['close'].unstack('symbol').dropna().iloc[-1]
    
    @property
    def cumm_returns(self):
        """
        Returns (DataFrame): columns are the "assets", index is the date and the values are the cummulative returns
            for the estimation period considered
        """
        rets_data = self.stock_data['logP'].unstack('symbol').iloc[::self.estimation_period].rolling(2).apply(lambda x: x[-1]-x[0], raw=True)
        self.cumm_returns_data = rets_data.dropna()
        return self.cumm_returns_data

    @property
    def linear_returns(self):
        """
        Returns (DataFrame): columns are the "assets", index is the date and the values are the linear returns
            for the estimation period considered
        """
        linear = self.stock_data['close'].unstack('symbol').iloc[::self.estimation_period].rolling(2).apply(lambda x: x[-1]/x[0]-1, raw=True)
        self.linear_returns_data = linear.dropna()
        return self.linear_returns_data

    def set_estimated_mu_cumm_rets(self, estimated_mean):
        """
        This sets the value of the mean vector value of the cumestimated_meanlative returns.
        """
        if not isinstance(estimated_mean, (pd.Series, list, np.ndarray)):
            raise TypeError("estimated_mean is not a series, list or array")
        # format into a series, in case it is an array
        if isinstance(estimated_mean, (np.ndarray, list)):
            estimated_mean = pd.Series(estimated_mean, index=assets)

        self.mu_cumm_rets = estimated_mean

    def set_estimated_cov_cumm_rets(self, estimated_cov):
        """
        This sets the value of the covariance matrix value of the cumestimated_covlative returns.
        """
        if not isinstance(estimated_cov, (pd.DataFrame, np.ndarray)):
            raise TypeError("estimated_cov_matrix is not a dataframe or array")
        # format into a series, in case it is an array
        if isinstance(estimated_cov, (np.ndarray, list)):
            estimated_cov = pd.Dataframe(estimated_cov,
                index=assets,
                columns=assets
                )

        self.cov_cumm_rets = estimated_cov

    def stats_cumm_rets_at_horizon(self):
        mean = self.mu_cumm_rets
        cov = self.cov_cumm_rets
        return mean*self.N_horizon, cov*self.N_horizon

    def stats_prices_at_horizon(self):
        mean = self.mu_cumm_rets
        cov = self.cov_cumm_rets

        K = np.diagonal(cov)
        mean_hori = self.latest_prices*np.exp(self.N_horizon*(mean + 0.5*K))
        Ln,Lm = np.meshgrid(mean_hori,mean_hori)
        cov_hori = Ln*Lm*(np.exp(self.N_horizon*cov)-1)
        return mean_hori, cov_hori

    def stats_linear_rets_at_horizon(self):
        mean_prices, cov_prices = self.stats_prices_at_horizon()
        inv_prices = 1/self.latest_prices
        mean_hori = inv_prices*mean_prices - 1

        inv_prices_n, inv_prices_m = np.meshgrid(inv_prices, inv_prices)
        cov_hori = inv_prices_n*cov_prices*inv_prices_n

        return mean_hori, cov_hori
