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

if __name__=='__main__':
    mkt = MarketData()
    mkt.update_complete_data_base()
    # mkt.save_crypto_data()


