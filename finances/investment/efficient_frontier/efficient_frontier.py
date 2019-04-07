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
    return np.sqrt(portfolio_volatility + L2_reg)


class EfficientFrontier(OriginalEF):
    mv_frontier = None

    def min_volatility(self):
        """
        Minimise volatility.

        :return: asset weights for the volatility-minimising portfolio
        :rtype: dict
        """
        args = (self.cov_matrix, self.gamma)
        result = sco.minimize(
            volatility,
            x0=self.initial_guess,
            args=args,
            method="SLSQP",
            bounds=self.bounds,
            constraints=self.constraints,
        )
        self.weights = result["x"]
        return dict(zip(self.tickers, self.weights))


    def efficient_return(self, target_return, market_neutral=False):
        """
        Calculate the 'Markowitz portfolio', minimising volatility for a given target return.

        :param target_return: the desired return of the resulting portfolio.
        :type target_return: float
        :param market_neutral: whether the portfolio should be market neutral (weights sum to zero),
                               defaults to False. Requires negative lower weight bound.
        :type market_neutral: bool, optional
        :raises ValueError: if ``target_return`` is not a positive float
        :return: asset weights for the Markowitz portfolio
        :rtype: dict
        """
        if not isinstance(target_return, float) or target_return < 0:
            raise ValueError("target_risk should be a positive float")

        args = (self.cov_matrix, self.gamma)
        target_constraint = {
            "type": "eq",
            "fun": lambda w: w.dot(self.expected_returns) - target_return,
        }
        # The equality constraint is either "weights sum to 1" (default), or
        # "weights sum to 0" (market neutral).
        if market_neutral:
            if self.bounds[0][0] is not None and self.bounds[0][0] >= 0:
                warnings.warn(
                    "Market neutrality requires shorting - bounds have been amended",
                    RuntimeWarning,
                )
                self.bounds = self._make_valid_bounds((-1, 1))
            constraints = [
                {"type": "eq", "fun": lambda x: np.sum(x)},
                target_constraint,
            ]
        else:
            constraints = self.constraints + [target_constraint]

        result = sco.minimize(
            volatility,
            x0=self.initial_guess,
            args=args,
            method="SLSQP",
            bounds=self.bounds,
            constraints=constraints,
        )
        self.weights = result["x"]
        return dict(zip(self.tickers, self.weights))

    def create_mv_frontier(self, n_points):

        min_vol_weigths = pd.Series(self.min_volatility())
        min_er = max(np.sum(min_vol_weigths*self.expected_returns.values),0)
        print(volatility(min_vol_weigths, self.cov_matrix, gamma=0))

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
        
        df['expected_returns'].plot(style='r-', ax=ax[0])

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
        fig = plt.figure()

        df = self.efficient_frontier

        # generate the random portfolios
        np.random.seed(42)
        n_assets = len(self.tickers)
        all_weights = np.zeros((num_portfolios, n_assets))
        ret_arr = np.zeros(num_portfolios)
        vol_arr = np.zeros(num_portfolios)
        sharpe_arr = np.zeros(num_portfolios)

        for x in range(num_portfolios):
            # Weights
            weights = np.array(np.random.random(n_assets))
            weights = weights/np.sum(weights)
            
            # Save weights
            all_weights[x,:] = weights
            
            # Expected return
            ret_arr[x] = np.sum( (self.expected_returns * weights ))
            
            # Expected volatility
            vol_arr[x] = volatility(weights, self.cov_matrix)
            
            # Sharpe Ratio
            sharpe_arr[x] = ret_arr[x]/vol_arr[x]


        ax = df.plot(x='volatility', y='expected_returns', style='k-')

        ax.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
        return fig