import pandas as p
import datetime
import pickle
import os
import numpy as np
import pylab as plt
import json
from finances.market import market_data as mkt_data


cfd, cfn = os.path.split(os.path.abspath(__file__))

def buy_all(trading_client, coin):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    eur_available = float(trading_client.account_balance(base=coin, quote="eur")['eur_available'])
    amount_to_buy = eur_available/current_price*0.9975
    trading_client.buy_market_order(amount=amount_to_buy, base=coin, quote="eur")

def sell_all(trading_client, coin):
    amount_to_sell = float(trading_client.account_balance(base=coin, quote="eur")['{}_available'.format(coin)])
    trading_client.sell_market_order(amount=amount_to_sell, base=coin, quote="eur")

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
    trading_client,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):


    with open(os.path.join(cfd, 'trade_bot_status.json')) as json_file:
        current_bot_status = json.load(json_file)

    reference_price = current_bot_status['reference_price']
    top_price = current_bot_status['top_price']
    bot_price = current_bot_status['bot_price']

    cash = float(trading_client.account_balance(base='btc', quote="eur")['eur_available'])

    if cash < 5:  # less than 1 euro
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
    print('Current position: {}'.format(position))

    if position == 'buy':
        buy_all(trading_client=trading_client, coin='btc')
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)
        print('bougth at {}'.format(current_price))

    elif position == 'sell':
        sell_all(trading_client=trading_client, coin='btc')
        reference_price = current_price
        bot_price = reference_price*(1-minimum_gain)
        top_price = reference_price*(1+pct_gap)
        print('sold at {}'.format(current_price))

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

    bot_status_file = os.path.join(cfd, 'trade_bot_status.json')
    with open(bot_status_file, 'w') as f:
        json.dump(current_bot_status, f)

if __name__=='__main__':
    import bitstamp.client as bts
    trading_client = bts.Trading(
       username='769101',
       key='mXt0zCJOzL49pGEw25uLneM5gqQ5weL4',
       secret='UmBn6XJ28s4Dz7EyjDYd6Fq3aFm9X7uj'
       )

    dynamic_stoploss_strategy(
    trading_client,
    current_price=float(trading_client.ticker(base='btc', quote='eur')['last']),
    pct_gap=0.035,
    minimum_gain=0.025,
    reinvest_gap=0.35
    )