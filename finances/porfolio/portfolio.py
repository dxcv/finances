import pandas as pd
import datetime
import pickle
import os

from market.market_data import MarketData

cfd, cfn = os.path.split(os.path.abspath(__file__))

PORTFOLIOS_DIRECTORY = cfd

class PortFolio():
    assets = {}
    assets_prices = {}
    assets_data = pd.DataFrame()
    values_data = pd.DataFrame()
    market_data = MarketData()
    profits_data = pd.DataFrame()

    def __init__(self, name, assets_prices):
        self.name = name
        self.assets_prices = assets_prices
        self.set_portfolio_directory()
        self.load_portfolio_assets_data()

    def set_portfolio_directory(self):
        directory = os.path.join(PORTFOLIOS_DIRECTORY, self.name)
        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.portfolio_directory = directory

    def load_portfolio_assets_data(self):
        data_csv = 'assets_allocation_data.csv'
        portfolio_data_path = os.path.join(self.portfolio_directory, data_csv)
        try:
            df = pd.read_csv(portfolio_data_path, index_col=0, parse_dates=True, infer_datetime_format=True)
            print('Loaded portfolio database from {}'.format(portfolio_data_path))
            self.assets_data = df
            self.assets = self.assets_data.iloc[-1].to_dict()
            self.values_data = self.get_values_data()
            # self.profits_data = self.get_profits()
            return df

        except FileNotFoundError:
            print('Data base not existent yet.')
            return

    def update_portfolio_assets(self, assets=None):
        assets_data = self.assets_data
        if assets is None:
            current_assets = self.assets
        else:
            current_assets = assets
        _temp_df = pd.DataFrame(
            data=current_assets,
            index=[datetime.datetime.now().replace(second=0, microsecond=0)]
        )

        # append this to the current database
        self.assets_data = assets_data.append(_temp_df)
        print('Portfolio assets updated')
        return self.assets_data

    def save_assets_data(self, output_name='assets_allocation_data'):
        self.assets_data.to_pickle(os.path.join(self.portfolio_directory, output_name+'.pkl'))
        self.assets_data.to_csv(os.path.join(self.portfolio_directory, output_name+'.csv'))
        print('Assets data base saved in {}\crypto_currencies'.format(self.portfolio_directory))

    def save_values_db(self, output_name='portfolio_value_data'):
        self.values_data.to_pickle(os.path.join(self.portfolio_directory, output_name+'.pkl'))
        self.values_data.to_csv(os.path.join(self.portfolio_directory, output_name+'.csv'))
        print('Portfolio value data saved in {}\crypto_currencies'.format(self.portfolio_directory))

    def get_full_asset_vs_price_df(self):
        asset_list = list(self.assets.keys())
        prices = self.market_data.get_crypto_price_history(symbols=asset_list)
        merged = prices.join(self.assets_data, lsuffix='_price', rsuffix='_quantity', how='outer')
        return merged.fillna(method='ffill').dropna()

    def get_values_data(self):
        prices_assets_df = self.get_full_asset_vs_price_df()
        value_df = pd.DataFrame()
        for asset in self.assets:
            value_df[asset] = prices_assets_df[asset+'_quantity']*prices_assets_df[asset+'_price']
        value_df['TOTAL'] = value_df.sum(axis=1)
        return value_df

    def update_data(self):
        self.values_data = self.get_values_data()
        self.profits_data = self.get_profits()

    def save_data(self):
        self.save_assets_data()
        self.save_values_db()

    def get_profits(self):
        prices_assets_df = self.get_full_asset_vs_price_df()
        profits_df = pd.DataFrame()
        for asset in self.assets:
            profits_df[asset] = (prices_assets_df[asset+'_price']-self.assets_prices[asset])/self.assets_prices[asset]
        self.profits_data = profits_df
        return profits_df

    def returns_data(self, symbols='TOTAL', offset='D'):
        """
        offset definition in http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        """
        portfolio_data = self.get_values_data()
        daily_data = portfolio_data.resample(offset).mean()
        return daily_data.pct_change()

    def weights_data(self):
        values =self.get_values_data()
        return values.multiply(1/values.TOTAL, axis=0)*100

    def insert_assets_at_date(self, assets, date):
        _temp_df = pd.DataFrame(data=assets, index=[date])
        new_df = pd.concat([_temp_df, self.assets_data]).sort_index()
        self.assets_data = new_df.fillna(value=0)
        return self.assets_data

    def relative_variation_since(self,
        n_days,
        start_date=None,
        time_scale=None,
        end_date=datetime.datetime.today()
        ):

        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=n_days)

        df = self.get_values_data()

        if time_scale is not None:
            df = df.resample(time_scale).mean()
        
        select_dates_df=df.ix[start_date:end_date]
        relative_change=select_dates_df.apply(lambda x: (x-x[0])/x[0])
        return relative_change

    def optimize_allocation(self, how='Sharpe', **kwargs):
        import portfolioopt as pfopt
        mkt = MarketData()
        returns = mkt.crypto_returns_history(symbols=list(self.assets.keys())).dropna(how='any')
        print(returns)

        if how == 'Sharpe':
            optimization_function = pfopt.tangency_portfolio
        
        elif how == 'Markowitz':
            optimization_function = pfopt.markowitz_portfolio
       
        avg_rets = returns.mean()
        cov_mat = returns.cov()
        weights_optimal = optimization_function(cov_mat=cov_mat, exp_rets=avg_rets, **kwargs)
        weights_optimal = pfopt.truncate_weights(weights=weights_optimal, min_weight=0.01)
        return weights_optimal



if __name__=='__main__':
    portfolio_assets = {
        'BTC': 0.007,
        'ETH': 2.14081,
        'XRP': 922.5,
        'ADA': 926,
        'XLM': 929.07,
        'LTC': 1.0,
        'TRX': 2760,
        'UBQ': 18.222,
        'BIS': 36.6,
        'IOTA': 47.553,
        'EMC2': 45,
        'FUN': 633.366,
        'ADST': 136.71
    }

    new_portfolio_assets = {
        'BTC': 0.08074255978,
        'ETH': 2.14081031,
        'LTC': 1.50000003,
        'XRP': 130,
        'DASH': 0.286593,
        'XMR': 1.32867,
        'IOTA': 47.553,
        'ADA': 0.073,
        'XLM': 279.07,
        'TRX': 0.237,
        'BCH': 0,
        'FUN': 2550.366,
        'EMC2': 45,
        'UBQ': 18.22222222,
        'BIS': 36.59233533,
        'ADST':   136.71
    }

    assets_effective_price = {
        'BTC': 0.1,
        'ETH': 454.96,
        'XRP': 0.772,
        'ADA': 0.404,
        'XLM': 0.378,
        'LTC': 208.23,
        'TRX': 0.0668,
        'UBQ': 5.7,
        'BIS': 3.48,
        'IOTA': 3.08,
        'EMC2': 0.769,
        'FUN': 0.0897,
        'ADST': 0.817   
    }

    import pylab as plt
    import seaborn as sns
    from pprint import pprint

    sns.set()
    
    myportfolio = PortFolio(
        name= 'PedroPortfolio',
        assets_prices = assets_effective_price
        )

    myportfolio.insert_assets_at_date(assets=new_portfolio_assets, date=datetime.datetime(2018,2,6))
    print(myportfolio.assets_data)


    p = myportfolio.get_values_data()
    print(p)
    p.plot()
    myportfolio.save_data()
    # result = myportfolio.update_data()
    # t = myportfolio.relative_variation_since(n_days=10)
    # print(t)
    # t.plot(style={'TOTAL':'--k'})
    # # plt.ylim([-1,2])
    plt.show()

    # weights = myportfolio.optimize_allocation(how='Sharpe')# target_ret=0.03)
    # print(weights)
