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
        min_er = np.sum(self.weights*self.expected_returns.values)

        max_er = max(self.expected_returns)
        er_list = np.linspace(min_er, max_er, n_points)
        mv_frontier = {'expected_returns': er_list, 'volatility': [], 'weights': []}

        for er in er_list:
            self.efficient_return(target_return=er, market_neutral=False)
            weights = self.clean_weights()
            vol = volatility(self.weights, self.cov_matrix, gamma=0)
            mv_frontier['volatility'].append(vol)
            mv_frontier['weights'].append(weights)

        self.mv_frontier = mv_frontier

        return mv_frontier


    def plot_mv_frontier(self):
        x = self.mv_frontier['volatility']
        y = self.mv_frontier['expected_returns']

        ax = plt.plot(x,y, '-o')
        return ax
