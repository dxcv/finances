# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 19:30:18 2017

@author: Pedro
"""

import logging
import socket
import sys

import bitstamp.client as bts
import time
import pandas as pd
import datetime

import os

lock_socket = None  # we want to keep the socket open until the very end of
                    # our script so we use a global variable to avoid going
                    # out of scope and being garbage-collected

def is_lock_free():
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_id = "hordeus.bitstamp_hf_data"   # this should be unique. using your username as a prefix is a convention
        lock_socket.bind('\0' + lock_id)
        logging.debug("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        # socket already locked, task must already be running
        logging.info("Failed to acquire lock %r" % (lock_id,))
        return False

n_trials = 0
while not is_lock_free():
    print('Socket busy... Trying again in 10 seconds...')
    time.sleep(10)
    n_trials+=1

    if n_trials>15:
        sys.exit()

print('Socket Free. Continuing to actual code.')

######################
# Real code
######################

start_time = datetime.datetime.now()
truncated_start_time = start_time.replace(minute=(30*(start_time.minute>30.0)+0))

cfd = os.path.dirname(os.path.realpath(__file__))

trading_client = bts.Trading(
       username='769101',
       key='2lAZXUmlwLQfhc80QPcHgFxbhvMSlmY6',
       secret='Z4yacXGzh7LrBcIUqdDjkOfvH5lEcyQZ'
       )

def update_price_data(prices_df):

    _new_data = {'btc': 0, 'eth': 0, 'ltc': 0, 'xrp':0, 'bch':0}

    for coin in list(_new_data.keys()):
        try:
            _new_data[coin] = float(trading_client.ticker(base=coin, quote='eur')['last'])
        except:
            print('Coin {} raised error'.format(coin))

    _temp_df = pd.DataFrame(
        data=_new_data,
        index=[datetime.datetime.now()])
    prices_df = prices_df.append(_temp_df)
    return prices_df

collect = True
while collect:
    pace = 0
    prices_df = pd.read_csv(
        os.path.join(cfd, 'bitstamp_high_frequency_data.csv'),
        index_col=0,
        parse_dates=True,
        infer_datetime_format=True
    )

    for pace in range(20):
        prices_df = update_price_data(prices_df)
        if (datetime.datetime.now()-truncated_start_time)>=datetime.timedelta(minutes=30):
            collect=False
            break
        time.sleep(20)

    prices_df.to_csv(os.path.join(cfd, 'bitstamp_high_frequency_data.csv'))
    print('Data saved at {}'.format(datetime.datetime.now()))

sys.exit()

