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

import pyfolio as pf


from crypto_analysis.crypto_data import get_quandl_data

def cal_returns(array):
    return array[-1]/array[0]

btc_usd = pd.read_csv('C:\\Users\\Pedro\\Dropbox\\repository\\projects\\finances.git\\data\\btc_usd.csv')

print(btc_usd.dropna())

btc_returns = btc_usd.rolling(window=2).apply(cal_returns).dropna()['avg_btc_price_usd']

out_of_sample = btc_returns.index[-40]

pf.create_returns_tear_sheet(
    returns=btc_returns,
    benchmark_rets=btc_returns,
    live_start_date=out_of_sample
)
