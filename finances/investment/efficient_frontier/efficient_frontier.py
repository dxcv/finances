"""
The ``efficient_frontier`` module houses the EfficientFrontier class, which
generates optimal portfolios for various possible objective functions and parameters.
"""

import warnings
import numpy as np
import pandas as pd
import scipy.optimize as sco
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier as OriginalEF



def volatility(weights, cov_matrix, gamma=0):
    """
    Calculate the volatility of a portfolio. This is actually a misnomer because
    the function returns variance, which is technically the correct objective
    function when minimising volatility.

    :param weights: asset weights of the portfolio
    :type weights: np.ndarray
    :param cov_matrix: the covariance matrix of asset returns
    :type cov_matrix: pd.DataFrame
    :param gamma: L2 regularisation parameter, defaults to 0. Increase if you want more
                  non-negligible weights
    :type gamma: float, optional
    :return: portfolio variance
    :rtype: float
    """
    L2_reg = gamma * (weights ** 2).sum()
    portfolio_volatility = np.dot(weights.T, np.dot(cov_matrix, weights))
    return portfolio_volatility + L2_reg


class EfficientFrontier(OriginalEF):
    mv_frontier = None

    def create_mv_frontier(self, n_points):

        min_vol_weigths = self.min_volatility()
        min_er = max(np.sum(self.weights*self.expected_returns.values),0)

        max_er = max(self.expected_returns)
        er_list = np.linspace(min_er, max_er, n_points)

        port_returns = []
        port_volatility = []
        stock_weights = []

        for er in er_list:
            self.efficient_return(target_return=er, market_neutral=False)
            weights = self.clean_weights()
            vol = volatility(self.weights, self.cov_matrix, gamma=0)
            port_returns.append(er)
            port_volatility.append(vol)
            stock_weights.append(weights)

        stock_weights = {k: [dic[k] for dic in stock_weights] for k in stock_weights[0]}
        # a dictionary for Returns and Risk values of each portfolio
        mv_dict = {
            'expected_returns': port_returns,
            'volatility': port_volatility,
            **stock_weights
            }

        # make a nice dataframe of the extended dictionary
        df = pd.DataFrame(mv_dict)

        self.efficient_frontier = df

        return df


    def plot_mv_frontier(self):
        fig, ax = plt.subplots(2,1, sharex=True)
        df = self.efficient_frontier
        df = df.set_index('volatility')
        
        df['expected_returns'].plot(style='-o', ax=ax[0])

        weights = df.drop('expected_returns', axis=1).T
        to_plot = weights.rolling(len(weights), min_periods=1).sum().T

        for col in to_plot.columns[::-1]:
            ax[1].fill_between(to_plot.index, 0, to_plot[col], label=col)

        ax[1].legend(ncol=4)

        return ax


    def create_portfolio_scatter(self,num_portfolios):
        # empty lists to store returns, volatility and weights of imiginary portfolios
        port_returns = []
        port_volatility = []
        stock_weights = []

        # set the number of combinations for imaginary portfolios
        num_assets = self.n_assets

        # populate the empty lists with each portfolios returns,risk and weights
        for single_portfolio in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights *= 1/np.sum(weights)
            returns = np.dot(weights, self.expected_returns)
            vol = volatility(weights, self.cov_matrix)
            port_returns.append(returns)
            port_volatility.append(vol)
            stock_weights.append(weights)

        # a dictionary for Returns and Risk values of each portfolio
        portfolio = {'Returns': port_returns,
                     'Volatility': port_volatility}

        # extend original dictionary to accomodate each ticker and weight in the portfolio
        for counter,symbol in enumerate(self.tickers):
            portfolio[symbol+' weight'] = [weight[counter] for weight in stock_weights]

        # make a nice dataframe of the extended dictionary
        df = pd.DataFrame(portfolio)

        # get better labels for desired arrangement of columns
        column_order = ['Returns', 'Volatility'] + [stock+' weight' for stock in self.tickers]

        # reorder dataframe columns
        df = df[column_order]

        return df

    def plot_scatter_efficient(self, num_portfolios):
        fig, ax = plt.subplots(1,1, sharex=True)
        x = self.mv_frontier['volatility']
        y = self.mv_frontier['expected_returns']
        
        ax.plot(x,y, 'k--')

        df_monte_carlo = self.create_portfolio_scatter(num_portfolios)
        df_monte_carlo.plot.scatter(x='Volatility', y='Returns', ax=ax)
        return ax
