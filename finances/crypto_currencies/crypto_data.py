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

# import plotly.offline as py
# import plotly.graph_objs as go
# import plotly.figure_factory as ff

import pylab as plt

cfd, cfn = os.path.split(os.path.abspath(__file__))

data_path = 'C:\\Users\\Pedro\\Dropbox\\repository\\projects\\finances.git\\finances\\crypto_currencies\\data'

def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = os.path.join(data_path, '{}.pkl'.format(quandl_id).replace('/','-'))
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

def get_json_data(json_url, poloniex_pair):
    '''Download and cache JSON data, return as a dataframe.'''
    cache_path = os.path.join(data_path, '{}.pkl'.format(poloniex_pair))
    try:        
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(json_url))
    except (OSError, IOError) as e:
        print('Downloading {}'.format(json_url))
        df = pd.read_json(json_url)
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(json_url, cache_path))
    return df


def get_btc_exchanges_data(column):
    # Pull pricing data for 3 more BTC exchanges
    exchanges = ['KRAKEN', 'COINBASE','BITSTAMP','ITBIT']

    full_exchange_data = {}

    for exchange in exchanges:
        exchange_code = 'BCHARTS/{}USD'.format(exchange)
        exchange_df = get_quandl_data(exchange_code)

        # removes all the zeros
        exchange_df.replace(0, np.nan, inplace=True)
        exchange_price = exchange_df[column]

        full_exchange_data[exchange] = exchange_price

    return pd.DataFrame(full_exchange_data)


def get_btc_price(column='Close'):
    full_exchange_data = get_btc_exchanges_data(column=column)
    full_exchange_data['Average'] = full_exchange_data.mean(axis=1)
    return full_exchange_data['Average'].dropna()


def get_crypto_data(
    poloniex_pair,
    start_date=datetime.strptime('2015-01-01', '%Y-%m-%d'),
    end_date=datetime.now(),
    period='Day'
    ):
    '''Retrieve cryptocurrency data from poloniex'''

    period_dict = {'Day': 86400, 'Hour':3600, 'Min': 60, 'Sec':1}
    base_poloniex_url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
    json_url = base_poloniex_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), period_dict[period])
    data_df = get_json_data(json_url, poloniex_pair)
    data_df = data_df.set_index('date')
    return data_df

if __name__=='__main__':
    df = get_btc_price(column='Close')
    df.close.plot()
    plt.show()
