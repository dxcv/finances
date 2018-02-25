# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 19:30:18 2017
 
@author: Pedro
"""
 
import bitstamp.client
from pprint import pprint
import time
import pandas as pd

public_client = bitstamp.client.Public()

import time
 
# Wait for 5 seconds
time.sleep(5)
 
trading_client = bitstamp.client.Trading(
       username='769101',
       key='jVoPUWeXacIrjzYIs99d9pe8jxEbv3U6',
       secret='m9DEG4zucVxMVp0vWyROpkJUBXKvkL0F'
       )

# print(trading_client.account_balance())
 
 
for k in range(100000):
    print(k, trading_client.ticker(base='bch', quote='btc'))  # Can access public methods
    # for k in dic_entry:
    #     bit_dic[k].append(dic_entry[k])
    # df = pd.DataFrame.from_dict(bit_dic)
    time.sleep(1)
    # df.to_csv('first_test.csv')