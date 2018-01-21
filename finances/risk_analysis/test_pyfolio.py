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

import pyfolio as pf
import pylab as plt

from market.market_data import MarketData

mkt = MarketData()

btc_returns = mkt.crypto_returns_history(symbols='BTC').dropna()
eth_returns = mkt.crypto_returns_history(symbols='XRP').dropna()

pf.create_full_tear_sheet(
    returns=eth_returns,
    benchmark_rets=btc_returns,
    live_start_date=btc_returns.index[-30]
)
