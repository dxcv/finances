"""
This is a copy of the analysis made in
https://blog.patricktriest.com/analyzing-cryptocurrencies-python/
"""

import os
import numpy as np
import pandas as pd
import pickle
import quandl
import datetime
import csv

from coinmarketcap import Market

COINMARKETCAP = Market()

cfd, cfn = os.path.split(os.path.abspath(__file__))

convert_name_dictionary={
    'BTC': 'bitcoin',
    'DASH': 'dash',
    'XMR': 'monero',
    'BCH': 'bitcoin-cash',
    'NEO': 'neo',
    'NEM': 'nem',
    'ETH': 'ethereum',
    'XRP': 'ripple',
    'LTC': 'litecoin',
    'ADA': 'cardano',
    'UBQ': 'ubiq',
    'BIS': 'bismuth',
    'IOTA': 'iota',
    'EMC2': 'einsteinium',
    'TRX': 'tron',
    'FUN': 'funfair',
    'XLM': 'stellar',
    'ADST': 'adshares',
    #
    'ICX': 'icon',
    'QTUM': 'qtum',
    'VEN': 'vechain',
    'XRB': 'raiblocks',
    'STEEM': 'steem',
    'STRAAT': 'stratis',
    'XVG': 'verge',
    # 'EOS': 'eos',
    # 'ONT': 'ontology'
}


class MarketData():
    data_base_path = os.path.join(cfd, 'data_base')
    crypto_dictionary = convert_name_dictionary
    crypto_data = pd.DataFrame()

    def __init__(self):
        db_name_csv = 'main_crypto_eur_database.csv'
        self.crypto_db_path = os.path.join(self.data_base_path, 'crypto_currencies', db_name_csv)
        self.load_crypto_data(currency='eur')

    def load_crypto_data(self, currency='eur'):
        print('Loaded crypto currency database from {}'.format(self.crypto_db_path))
        self.crypto_data = pd.read_csv(self.crypto_db_path, index_col=0, parse_dates=True, infer_datetime_format=True)
        return self.crypto_data

    def get_current_coin_price(self, crypto_code, currency='eur'):
        crypto_name = self.crypto_dictionary[crypto_code]
        try:
            coin = COINMARKETCAP.ticker(crypto_name, convert='eur')
            value = float(coin[0]['price_{}'.format(currency)])
        except:
            value = np.nan
            print('!!!! {} not working.'.format(crypto_name))
        return value

    def get_coin_full_data(self, crypto_code):
        crypto_name = self.crypto_dictionary[crypto_code]
        coin = COINMARKETCAP.ticker(crypto_name, convert='eur')
        return coin[0]

    def get_total_market_cap(self, currency='eur'):
        try:
            total_market = COINMARKETCAP.stats(convert='EUR')
            value = total_market['total_market_cap_{}'.format(currency)]
        except:
            value = np.nan
            print('!!!! Total Market Cap not working.')
        return value

    def update_coin_full_data(self, crypto_code):
        coin_path = os.path.join(self.data_base_path, 'crypto_currencies', '{}_full_data.csv'.format(crypto_code))
        coin_full_data = self.get_coin_full_data(crypto_code)
        
        try:
            coin_full_data['']=datetime.datetime.now().replace(second=0, microsecond=0)
            sorted_keys = sorted(list(coin_full_data.keys()))
            with open(coin_path, 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=sorted_keys, dialect='excel')
                writer.writerow(coin_full_data)

        except FileNotFoundError:
            data_coin_df = pd.DataFrame()
            _temp_df = pd.DataFrame(
                data=coin_full_data,
                index=[datetime.datetime.now().replace(second=0, microsecond=0)])
            data_coin_df = data_coin_df.append(_temp_df)
            data_coin_df.to_csv(coin_path)
            print('Created full database for {}'.format(crypto_code))


    def update_market_price_db(self):
        data_base = self.crypto_data
        current_prices = {}
        for coin in self.crypto_dictionary:
            current_prices[coin] = self.get_current_coin_price(coin, currency='eur')

        # add the total market capitalization data
        current_prices['TotalMarketCap'] = self.get_total_market_cap(currency='eur')

        # start organizing data to write csv
        current_prices['']=datetime.datetime.now().replace(second=0, microsecond=0)
        sorted_keys = sorted(list(current_prices.keys()))

        if sorted_keys == LISTOFKEYSFROMCSV:
            with open(self.crypto_db_path, 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=sorted_keys, dialect='excel')
                writer.writerow(current_prices)

        else:
            self.load_crypto_data()
            _temp_df = pd.DataFrame(
                index=[datetime.datetime.now().replace(second=0, microsecond=0)],
                data=current_prices.POP('')
                )
            self.crypto_data = data_base.append(_temp_df)
            self.save_crypto_data


    def update_complete_data_base(self):
        self.update_market_price_db()

        for coin in self.crypto_dictionary:
            try:
                self.update_coin_full_data(crypto_code=coin)
            except:
                print('Error in the {} full data update'.format(coin))
                continue


    def load_coin_full_data_base(self, crypto_code):
        coin_path = os.path.join(self.data_base_path, 'crypto_currencies', '{}_full_data.csv'.format(crypto_code))
        data_coin_df = pd.read_csv(
            coin_path,
            index_col=0,
            parse_dates=True,
            infer_datetime_format=True)
        return data_coin_df

    def save_crypto_data(self, output_name='main_crypto_eur_database'):
        self.crypto_data.to_pickle(os.path.join(self.data_base_path, 'crypto_currencies', output_name+'.pkl'))
        self.crypto_data.to_csv(os.path.join(self.data_base_path, 'crypto_currencies', output_name+'.csv'))
        print('Crypto currency data base saved in {}\crypto_currencies'.format(self.data_base_path))

    def get_crypto_price_data(self, symbols, start_date=datetime.datetime(2010,1,1), end_date=datetime.datetime.now()):
        return self.crypto_data[symbols].loc[start_date:end_date]

    def get_price_at_date(self, symbols, date):
        crypto_data = self.crypto_data[symbols]
        return crypto_data.loc[:date].iloc[-1]

    def crypto_returns_data(self, symbols=None, time_step='D', start_date=datetime.datetime(2013,1,1), end_date=datetime.datetime.now()):
        """
        offset definition in http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        """
        if symbols is None:
            symbols = list(self.crypto_dictionary.keys())
        resampled_data = self.crypto_data[symbols].resample(time_step).mean()

        resampled_data = resampled_data.loc[start_date:end_date]

        return resampled_data.pct_change()#.dropna()

    def cummulative_variation(
        self,
        symbols=None,
        n_days=0,
        start_date=None,
        time_scale=None,
        end_date=datetime.datetime.today()
        ):

        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=n_days)

        if symbols is None:
            symbols = list(self.crypto_dictionary.keys())

        df = self.get_crypto_price_data(symbols=symbols)

        if time_scale is not None:
            df = df.resample(time_scale).mean()

        select_dates_df=df.ix[start_date:end_date]
        relative_change=select_dates_df.apply(lambda x: (x-x[0])/x[0])
        return relative_change

    def fit_returns_dist(
        self,
        symbol,
        time_frame='D',
        N_steps=1,
        dist = 't-student',
        start_date=datetime.datetime(2000, 1, 1, 1, 1) ,
        end_date=datetime.datetime.now()):

        from scipy.stats import norm, t
        if dist == 't-student':
            fit_dist = t
        elif dist == 'normal':
            fit_dist = norm
        rets = self.crypto_returns_data(symbols=symbol, time_step=time_frame)
        rets=rets.iloc[start_date:rets.index<end_date].dropna()

        # MLE of the sample for a normal distribution (to be improved)
        dist_fit_params = fit_dist.fit(rets)
        return dist_fit_params


if __name__=='__main__':
    import pylab as plt

    import seaborn as sns

    sns.set()

    mkt = MarketData()

    a = mkt.get_crypto_price_data('BTC')
    a.plot()
    print(a)
    plt.show()

    # date=datetime.datetime(2018, 3, 29)
    # print(mkt.get_price_at_date(symbols='BTC', date=date))
    # print(mkt.get_price_at_date(symbols='DASH', date=date))
    # # mu, std = mkt.normal_fit_returns('ETH')
    # # print(mu)
    # # mkt.update_complete_data_base()
    # df = mkt.cummulative_variation(n_days=10)
    # df.plot()

    # # mkt.save_crypto_data()
    # # print(mkt.crypto_data)

    # plt.show()

