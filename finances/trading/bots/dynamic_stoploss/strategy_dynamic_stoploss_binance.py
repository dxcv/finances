import sys
import os

cfp, cfn = os.path.split(os.path.abspath(__file__))

sys.path.append(os.path.join(cfp, '..', '..', '..', '..'))   # <--------- this is to run in pythonanywhere

import json
import time
from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy
from binance.exceptions import BinanceAPIException

def buy_all(trading_client, coin, cash_quantity):

    # get all the prices
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])

    # extract the relevant prices
    current_btc_price = price_list['BTCUSDT']
    current_price_in_btc= price_list[coin+'BTC']
    current_price_in_usd = (current_price_in_btc*current_btc_price)

    # calculate the amount of both coin and btc to buy
    amount_to_buy = cash_quantity/current_price_in_usd
    btc_to_buy = cash_quantity/current_btc_price

    bought_btc=False
    bought_coin=False
    counter=0

    # first buy the corresponding amount of btc
    while not bought_btc and btc_to_buy>0 and counter < 20:
        try:
            trading_client.order_market_buy(
                symbol='BTCUSDT',
                quantity=round(btc_to_buy, 5)
            )
            bought_btc=True
            # print('Bought {0} BTC'.format(btc_to_buy))
        except BinanceAPIException as e:
            btc_to_buy*=0.9975
            counter+=1

    # then buy the corresponding amount of the required coin
    time.sleep(2)  # wait a bit for the previous transaction take place
    rounder=5
    counter=0

    while not bought_coin and amount_to_buy>0.0 and counter<20:
        try:
            trading_client.order_market_buy(
                symbol=coin+'BTC',
                quantity=round(amount_to_buy, rounder)
            )
            bought_coin=True
            print('Bought {0} {1} at {2} USD'.format(amount_to_buy, coin, current_price_in_usd))
        except BinanceAPIException as e:
            if 'LOT_SIZE' in str(e):
                rounder -=1
            if 'insufficient balance' in str(e):
                amount_to_buy*=0.9975
                counter+=1


def sell_all(trading_client, coin):
    # get all the prices
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])

    # extract the relevant prices
    current_btc_price = price_list['BTCUSDT']
    current_price_in_btc= price_list[coin+'BTC']
    current_price_in_usd = (current_price_in_btc*current_btc_price)

    # calculate the sell
    coin_available = float(trading_client.get_asset_balance(asset=coin)['free'])
    amount_to_sell = coin_available

    sold_coin=False
    rounder = 5
    sold_btc=False
    counter=0

    # first sell all to btc
    while not sold_coin and amount_to_sell>0 and counter <20:
        try:
            trading_client.order_market_sell(
                symbol=coin+'BTC',
                quantity=round(amount_to_sell, rounder)
            )
            sold_coin=True
            print('Sold {0} {1} at {2} USD'.format(amount_to_sell, coin, current_price_in_usd))
        except BinanceAPIException as e:
            if 'LOT_SIZE' in str(e):
                rounder -=1
            if 'insufficient balance' in str(e):
                counter+=1
                amount_to_sell*=0.9975

    # then sell all btc to usd
    time.sleep(2)  # wait a bit for the previous transaction take place

    btc_available = float(trading_client.get_asset_balance(asset='btc')['free'])
    btc_to_sell = btc_available
    while not sold_btc and btc_to_sell>0:
        try:
            trading_client.order_market_sell(
                symbol='BTCUSDT',
                quantity=round(btc_to_sell, 5)
            )
            sold_btc=True
            # print('Sold {0} BTC'.format(btc_to_sell))
        except BinanceAPIException as e:
            btc_to_sell=btc_to_sell*0.9975

    return amount_to_sell

def check_cash(trading_client, coin, stored_cash):
    # get all the prices
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])

    # extract the relevant prices
    current_btc_price = price_list['BTCUSDT']
    current_price_in_btc= price_list[coin+'BTC']
    current_price_in_usd = (current_price_in_btc*current_btc_price)

    #
    coin_available = float(trading_client.get_asset_balance(asset=coin)['free'])
    value = coin_available*current_price_in_usd
    if value < 5:  # se o valor for inferior a 5€
        value = 0

    if stored_cash==0 and value == 0:
        # in this case, there was a stoploss sell transaction and we need to check for how much
        last_transaction_quantity=float(trading_client.get_my_trades(
            symbol=coin+'BTC',
            limit=1)[0]['qty']
        )
        return last_transaction_quantity*current_price_in_usd
    elif stored_cash>0 and value >0:
        # in this case, there was a stoploss buy transaction
        return 0
    else:
        return stored_cash
    return cash


def dynamic_stoploss_binance_bot(
    trading_client,
    coin,
    bot_status_json_path,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.5
    ):

    with open(bot_status_json_path) as json_file:
        binance_bot_status = json.load(json_file)

    current_bot_status = binance_bot_status[coin]

    current_bot_status['cash'] = check_cash(trading_client, coin, stored_cash=current_bot_status['cash'])

    current_bot_status, position = dynamic_stoploss_strategy(
        status_dict=current_bot_status,
        cash=current_bot_status['cash'],
        current_price=current_price,
        pct_gap=pct_gap,
        minimum_gain=minimum_gain,
        reinvest_gap=reinvest_gap
        )

    print('Position: '+position)

    # perform the actual sell/buy options
    if position == 'buy':
        buy_all(trading_client=trading_client, coin=coin, cash_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all(trading_client=trading_client, coin=coin)*current_price

    # save the new bot status dict
    binance_bot_status[coin] = current_bot_status


    if position=='update_stoploss_sell':
        print('Create stoploss sell order of {} at {}'.format(coin, current_bot_status['stoploss_price']))

    elif position=='update_stoploss_buy':
        print('Create stoploss buy order of {} at {}'.format(coin, current_bot_status['stoploss_price']))


    with open(bot_status_json_path, 'w') as f:
        json.dump(binance_bot_status, f, sort_keys=True, indent=4)

if __name__=='__main__':
    from binance.client import Client
    from pprint import pprint

    api_key='QuJSzBd0O8Uube4sOr1DOySMsZWsKC5EpjFYP12FZPO0WEQbBrjjU8N5kVPb5Qkt'
    api_secret = 'XiPd9cc3VHDl5sa0juCYs27kVPipPEMkddmHxYol6pGuOWgLsZK4cH7SwpJf4Qev'
    client = Client(api_key, api_secret)
    all_tickers = client.get_all_tickers()
    price_list = {}
    for pair in client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])
    pprint(price_list)
    # pprint(client.get_all_tickers())