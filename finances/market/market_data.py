"""
This is a copy of the analysis made in
https://blog.patricktriest.com/analyzing-cryptocurrencies-python/
"""

import os
import numpy as np
import pandas as pd
import pickle
import quandl
from datetime import datetime

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
    'ADST': 'adshares'
}


class MarketData():
    data_base_path = os.path.join(cfd, 'data_base')
    crypto_dictionary = convert_name_dictionary
    crypto_eur_db = pd.DataFrame()

    def __init__(self):
        self.crypto_eur_db = self.load_crypto_data(currency='eur')


    def load_crypto_data(self, currency='eur'):
        db_name_csv = 'main_crypto_{}_database.csv'.format(currency)
        crypto_db_path = os.path.join(self.data_base_path, 'crypto_currencies', db_name_csv)
        print('Loaded crypto currency database from {}'.format(crypto_db_path))
        return pd.read_csv(crypto_db_path, index_col=0, parse_dates=True, infer_datetime_format=True)
        

    def get_coin_price(self, crypto_code, currency='eur'):
        crypto_name = self.crypto_dictionary[crypto_code]
        coin = COINMARKETCAP.ticker(crypto_name, convert='eur')
        value = coin[0]['price_{}'.format(currency)]
        return float(value)

    def get_total_market_cap(self, currency='eur'):
        total_market = COINMARKETCAP.stats(convert='EUR')
        return total_market['total_market_cap_{}'.format(currency)]

    def update_market_eur_price(self):
        data_base = self.crypto_eur_db
        _temp_df = pd.DataFrame(index=[datetime.now().replace(second=0, microsecond=0)])

        # add the data for all the crypto currencies
        for coin in self.crypto_dictionary:
            _temp_df[coin] = self.get_coin_price(coin, currency='eur')
            print('{} price data updated'.format(coin))

        # add the total market capitalization data
        _temp_df['TotalMarketCap'] = self.get_total_market_cap(currency='eur')
        print('TotalMarketCap value data updated')

        # append this to the current database
        self.crypto_eur_db = data_base.append(_temp_df)
        return self.crypto_eur_db 

    def save_crypto_eur_db(self, output_name='main_crypto_eur_database'):
        self.crypto_eur_db.to_pickle(os.path.join(self.data_base_path, 'crypto_currencies', output_name+'.pkl'))
        self.crypto_eur_db.to_csv(os.path.join(self.data_base_path, 'crypto_currencies', output_name+'.csv'))
        print('Crypto currency data base saved in {}\crypto_currencies'.format(self.data_base_path))

    def get_crypto_price_history(self, symbols):
        if isinstance(symbols, str):
            return self.crypto_eur_db[[symbols]]
        else:
            return self.crypto_eur_db[symbols]

    def get_crypto_returns_history(self, symbols, offset='D'):
        """
        offset definition in http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        """
        daily_data = self.crypto_eur_db[symbols].resample(offset).mean()
        return daily_data.pct_change()

if __name__=='__main__':
    import pylab as plt

    mkt = MarketData()

    mkt.update_market_eur_price()

    print(mkt.crypto_eur_db)
    db = mkt.get_crypto_returns_history(list(convert_name_dictionary.keys()))
    db.dropna(how='any').boxplot()

    mkt.save_crypto_eur_db()

    plt.show()

