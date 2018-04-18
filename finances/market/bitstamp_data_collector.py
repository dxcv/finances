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


def create_bitstamp_data_chunk(n_values, time_step, session_period):
    """
    Creates a df with n_values of lines with data collected each time_step (in seconds):

    n_values (int): number of values we want to collect
    time_step (float): step between values in seconds

    Returns:
    df (DataFrame): df with index the times of the data and the collumns each coin pair price
    """

    prices_data = []
    times_list = []

    for k in range(n_values):
        times_list.append(datetime.datetime.now())
        prices_data.append(bitstamp_current_prices())
        if (time.time() - start_time) >= session_period-time_step:
            break
        time.sleep(time_step)
        
    data_chunk = pd.DataFrame(
        data=prices_data,
        index=times_list)

    return data_chunk


def update_bitstamp_data(new_data_chunk):

    bitstamp_csv_path = os.path.join(exchanges_data_path, 'bitstamp_high_frequency_data.csv')

    # if not os.path.exists(bitstamp_csv_path):

    prices_df = pd.read_csv(
        bitstamp_csv_path,
        index_col=0,
        parse_dates=True,
        infer_datetime_format=True
    )

    # add to database and save the csv
    prices_df.append(new_data_chunk).to_csv(bitstamp_csv_path)
    print('Data saved at {}'.format(datetime.datetime.now()))


def collect_bistamp_data(collection_step=30, saving_step=300, session_time=600):
    """
    The function to run the data collection and save it.
    """
    number_saves = int(session_time/saving_step)
    number_collections = int(saving_step/collection_step)
    for chunk_no in range(number_saves):
        data_chunk=create_bitstamp_data_chunk(
            n_values=number_collections,
            time_step=collection_step,
            session_period=session_time)
        update_bitstamp_data(data_chunk)


if __name__=='__main__':
    global start_time
    start_time = time.time()
    stop_python=False

    print('Session open at: {}'.format(datetime.datetime.now()))
    from time import sleep
    collect_bistamp_data()
    print('Session closed at: {}'.format(datetime.datetime.now()))
    exit(0)