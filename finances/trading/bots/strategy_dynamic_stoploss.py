import pandas as p
import datetime
import pickle
import os
import numpy as np
import pylab as plt
import json
from finances.market import market_data as mkt_data


cfd, cfn = os.path.split(os.path.abspath(__file__))


def decision_short(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision = 'hold'

    if current_price > top_price:
        decision = 'buy'

    elif current_price < bot_price:
        bot_price = current_price

    elif current_price > (reference_price-abs((reference_price-bot_price))*0.5) and current_price < reference_price*(1 - minimum_gain):
        decision = 'buy'

    return decision, top_price, bot_price


def decision_long(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision='hold'

    if current_price<bot_price:
        decision='sell'

    elif current_price>top_price:
        top_price=current_price

    elif current_price<(reference_price+abs((reference_price-top_price))*0.5) and current_price>reference_price*(1+minimum_gain):
        decision='sell'

    return decision, top_price, bot_price


def dynamic_stoploss_strategy(
    current_status_file,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):


    with open(os.path.join(cfd, 'bot_status.json')) as json_file:
        current_bot_status = json.load(json_file)


    reference_price = current_bot_status['reference_price']
    top_price = current_bot_status['top_price']
    bot_price = current_bot_status['bot_price']


    #### GET MONEY FROM BITSTAMP
    cash = 1
    ####

    if cash < 1:  # less than 1 euro
        decision_strategy = decision_long

    else:
        decision_strategy = decision_short

    position, top_price, bot_price = decision_strategy(
        current_price=current_price,
        minimum_gain=minimum_gain,
        reference_price=current_bot_status['reference_price'],
        top_price=current_bot_status['top_price'],
        bot_price=current_bot_status['bot_price'],
        )

    if position == 'buy':
        #### ORDER BUY
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif position == 'sell':
        #### ORDER SELL
        reference_price = current_price
        bot_price = reference_price*(1-minimum_gain)
        top_price = reference_price*(1+pct_gap)

    # reinvest?
    elif current_price > reference_price*(1+reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif current_price < reference_price*(1-reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1+pct_gap)
        top_price = reference_price*(1-minimum_gain)

    current_bot_status['reference_price'] = reference_price
    current_bot_status['top_price'] = top_price
    current_bot_status['bot_price'] = bot_price

    bot_status_file = os.path.join(cfd, 'bot_status.json')
    with open(bot_status_file, 'w') as f:
        json.dump(current_bot_status, f)

