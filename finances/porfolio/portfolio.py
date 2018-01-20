import pandas as pd
import datetime
import pickle
import os

from market.market_data import MarketData

cfd, cfn = os.path.split(os.path.abspath(__file__))

PORTFOLIOS_DIRECTORY = cfd

class PortFolio():
    assets = {}
    assets_db = pd.DataFrame()
    value_db = pd.DataFrame()
    market_data = MarketData()

    def __init__(self, name, assets):
        self.name = name
        self.assets = assets
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
            self.assets_db = df
            return df
        except FileNotFoundError:
            print('Data base not existent yet.')
            return

    def update_portfolio_assets(self, assets=None):
        assets_data = self.assets_db
        if assets is None:
            current_assets = self.assets
        else:
            current_assets = assets
        _temp_df = pd.DataFrame(
            data=current_assets,
            index=[datetime.datetime.now().replace(second=0, microsecond=0)]
        )

        # append this to the current database
        self.assets_db = assets_data.append(_temp_df)
        print('Portfolio assets updated')
        return self.assets_db

    def save_assets_db(self, output_name='assets_allocation_data'):
        self.assets_db.to_pickle(os.path.join(self.portfolio_directory, output_name+'.pkl'))
        self.assets_db.to_csv(os.path.join(self.portfolio_directory, output_name+'.csv'))
        print('Assets data base saved in {}\crypto_currencies'.format(self.portfolio_directory))

    def save_values_db(self, output_name='portfolio_value_data'):
        self.value_db.to_pickle(os.path.join(self.portfolio_directory, output_name+'.pkl'))
        self.value_db.to_csv(os.path.join(self.portfolio_directory, output_name+'.csv'))
        print('Portfolio value data saved in {}\crypto_currencies'.format(self.portfolio_directory))

    def get_full_asset_vs_price_df(self):
        asset_list = list(self.assets.keys())
        prices = self.market_data.get_crypto_price_history(symbols=asset_list)
        merged = prices.join(self.assets_db, lsuffix='_price', rsuffix='_quantity', how='outer')
        return merged.fillna(method='ffill').dropna()

    def get_portfolio_value_df(self):
        prices_assets_df = self.get_full_asset_vs_price_df()
        value_df = pd.DataFrame()
        for asset in self.assets:
            value_df[asset] = prices_assets_df[asset+'_quantity']*prices_assets_df[asset+'_price']
        value_df['TOTAL'] = value_df.sum(axis=1)
        return value_df

    def update_portfolio_value(self, save_market=False):
        self.market_data.update_market_eur_price()
        if save_market:
            self.market_data.save_crypto_eur_db()
        self.update_portfolio_assets(assets=self.assets)
        value_db = self.get_portfolio_value_df()
        self.value_db = value_db
        return value_db

    def update_and_save_portfolio(self):
        updated_value = self.update_portfolio_value(save_market=True)
        self.save_assets_db()
        self.save_values_db()
        return updated_value

    def get_crypto_returns_history(self, symbols='TOTAL', offset='D'):
        """
        offset definition in http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        """
        portfolio_data = self.get_portfolio_value_df()
        daily_data = portfolio_data.resample(offset).mean()
        return daily_data.pct_change()

    def extend_assets_value_from(self, date):
        self.assets_db = pd.DataFrame(data=self.assets, index=[date])
        full_db = self.get_portfolio_value_df()
        return full_db

    def cummulative_variation(self,
        n_days,
        start_date=None,
        time_scale=None,
        end_date=datetime.datetime.today()
        ):

        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=n_days)

        df = self.get_portfolio_value_df()

        if time_scale is not None:
            df = df.resample(time_scale).mean()
        
        select_dates_df=df.ix[start_date:end_date]
        relative_change=select_dates_df.apply(lambda x: (x-x[0])/x[0])
        return relative_change


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

    import pylab as plt
    from pprint import pprint
    
    myportfolio = PortFolio(
        assets = portfolio_assets,
        name= 'PedroPortfolio'
        )

    result = myportfolio.cummulative_variation(n_days=10)
    print(result)
    result.plot()
    plt.show()

