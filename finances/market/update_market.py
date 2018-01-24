import os
import numpy as np
import pandas as pd
import pickle
import quandl
import datetime

from market.market_data import MarketData

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

if __name__=='__main__':
    mkt = MarketData()
    mkt.update_market_eur_price()
    mkt.save_crypto_eur_db()


