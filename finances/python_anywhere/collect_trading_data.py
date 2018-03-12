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
        lock_id = "my-username.my-task-name"   # this should be unique. using your username as a prefix is a convention
        lock_socket.bind('\0' + lock_id)
        logging.debug("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        # socket already locked, task must already be running
        logging.info("Failed to acquire lock %r" % (lock_id,))
        return False

if not is_lock_free():
    sys.exit()


######################
# Real code
######################

cfd = os.path.dirname(os.path.realpath(__file__))

price_list = {'btc': [], 'eth': [], 'ltc': [], 'xrp':[], 'bch':[]}
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
        df.to_csv(os.path.join(cfd, 'bitstamp_data_trading.csv'))
        save_data=0
    time.sleep(30)



