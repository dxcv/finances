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

price_list = {'btc': [], 'eth': [], 'ltc': [], 'xrp':[]}
times = []
save_data = 0

trading_client = bts.Trading(
       username='769101',
       key='2lAZXUmlwLQfhc80QPcHgFxbhvMSlmY6',
       secret='Z4yacXGzh7LrBcIUqdDjkOfvH5lEcyQZ'
       )

while True:
    for coin in list(price_list.keys()):
        try:
            current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
        except:
            print('Coin {} raised error'.format(coin))

        price_list[coin].append(current_price)

    times.append(datetime.datetime.now())

    save_data+=1

    # save_data:
    if save_data>=60:
        print('Data saved at {}.'.format(datetime.datetime.now()))
        df = pd.DataFrame(index=times, data=price_list)
        df.to_csv(os.path.join(cfd, 'prices_data_trading.csv'))
        save_data=0
    time.sleep(10)



