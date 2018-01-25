import os
import numpy as np
import pandas as pd
import pickle
import quandl
import datetime

import sys
cfd, cfn = os.path.split(os.path.abspath(__file__))
sys.path.append(cfd)

from market_data import MarketData

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
    mkt.update_complete_data_base()
    mkt.save_crypto_eur_db()


