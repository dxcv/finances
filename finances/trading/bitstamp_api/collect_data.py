# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 19:30:18 2017

@author: Pedro
"""

import bitstamp.client as bts
import time
import pandas as pd
import datetime

import os


cfd = os.path.dirname(os.path.realpath(__file__))

trading_client = bts.Trading(
       username='769101',
       key='2lAZXUmlwLQfhc80QPcHgFxbhvMSlmY6',
       secret='Z4yacXGzh7LrBcIUqdDjkOfvH5lEcyQZ'
       )

def update_price_data(prices_df)
    prices_df = pd.read_csv(
        data_path,
        index_col=0,
        parse_dates=True,
        infer_datetime_format=True
    )

    _new_data = {'btc': [], 'eth': [], 'ltc': [], 'xrp':[]}

    for coin in list(_new_data.keys()):
        try:
            current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
        except:
            print('Coin {} raised error'.format(coin))

    _temp_df = pd.DataFrame(
        data=current_price,
        index=[datetime.datetime.now()])
    prices_df = prices_df.append(_temp_df)
    return prices_df


while True:
    pace = 0
    prices_df = pd.read_csv(
        os.path.join(cfd, 'prices_data_trading.csv'),
        index_col=0,
        parse_dates=True,
        infer_datetime_format=True
    )

    for pace in range(10):
        prices_df = update_price_data(prices_df)
        time.sleep(3)

    df.to_csv(os.path.join(cfd, 'prices_data_trading.csv'))

    



