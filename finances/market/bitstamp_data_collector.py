# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 19:30:18 2017

@author: Pedro
"""

import bitstamp.client as bts
import time
import pandas as pd
import datetime
import numpy as np


import os

cfd = os.path.dirname(os.path.realpath(__file__))

exchanges_data_path = os.path.join(cfd, 'data_base', 'exchanges')

def bitstamp_current_prices():

    bitstamp_public = bts.Public()

    current_prices = {
    'btc-eur': 0, 'eth-eur': 0, 'ltc-eur': 0, 'xrp-eur':0, 'bch-eur':0,
    'eth-btc': 0, 'ltc-btc': 0, 'xrp-btc':0, 'bch-btc':0,
    }

    for coin_pair in list(current_prices.keys()):
        base=coin_pair.split('-')[0]
        quote=coin_pair.split('-')[1]
        try:
            coin_pair_price=float(bitstamp_public.ticker(base=base, quote=quote)['last'])
            current_prices[coin_pair] = round(coin_pair_price, 6)
        except:
            current_prices[coin_pair] = np.nan
            print('Coin pair {} raised error at time {}'.format(coin_pair, datetime.datetime.now()))

    return current_prices


def update_prices_csv(filename, prices_dict):
    pair_order = [
        'bch-btc','bch-eur','btc-eur','eth-btc','eth-eur',
        'ltc-btc','ltc-eur','xrp-btc','xrp-eur'
    ]
    list_to_write=[datetime.datetime.now()]+[prices_dict[pair] for pair in pair_order]
    string_to_write=",".join(map(str, list_to_write))

    print(string_to_write)

    with open(filename, 'a') as csv_file:
        csv_file.write(string_to_write+"\n")


def collect_bistamp_data():
    """
    The function to run the data collection and save it.
    """
    prices_data = bitstamp_current_prices()
    bitstamp_csv_path = os.path.join(exchanges_data_path, 'bitstamp_high_frequency_data.csv')
    update_prices_csv(bitstamp_csv_path, prices_data)
    print('Data saved at: {}'.format(datetime.datetime.now()))


if __name__=='__main__':
    collect_bistamp_data()