import sys
import os

cfp, cfn = os.path.split(os.path.abspath(__file__))

sys.path.append(os.path.join(cfp, '..', '..', '..', '..'))   # <--------- this is to run in pythonanywhere

import json
import time
from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy
from binance.exceptions import BinanceAPIException
from binance.client import Client

# get all the prices
# PRICE_LIST={}
# for pair in trading_client.get_all_tickers():
#     PRICE_LIST[pair['symbol']] = float(pair['price'])



td = Client(
    api_key='69SJ6W75YXxMqeM2uOHsYPidRHHc1tDuVa723QjcP7p8xKQOCvqi80QnoYoWFqdM',
    api_secret='6n3h0d7FvGiWTjF8Tm3NskURNpa2NnXbmqQfDinwOV0buPzE2W4aFDefkxpkgSco'
    )

# td.order_limit_buy(symbol='XLMUSDT', quantity=10, price=0.06, stopPrice=0.059)
# from pprint import pprint
# pprint(td.get_exchange_info())
# td.create_order(symbol='ADAUSDT', side='BUY', type='STOP_LOSS_LIMIT', quantity=200.0, price=0.08, stopPrice=0.079,timeInForce='GTC')
print(td.get_asset_balance(asset='ADA'))
exit(0)

def buy_all(trading_client, coin, cash_quantity):

    # extract the relevant prices
    current_btc_price = PRICE_LIST['BTCUSDT']
    current_price_in_btc= PRICE_LIST[coin+'BTC']
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
    # extract the relevant prices
    current_btc_price = PRICE_LIST['BTCUSDT']
    current_price_in_btc= PRICE_LIST[coin+'BTC']
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

def update_stoploss(trading_client, coin, price, cash=0):
    symbol=coin+'USDT'
    # first cancel the existing order
    orders = trading_client.get_all_orders(symbol)
    trading_client.cancel_order(symbol=symbol, orderId=orders[0]['orderId'])

    # quantity to buy:
    if cash!=0:
        quantity = cash/price
        order_type = 'BUY'

    # quantity to sell:
    else:
        balance = trading_client.get_asset_balance(asset=coin)
        quantity = float(balance['free'])

    # order
    trading_client.create_order(
        symbol=coin+'USDT',
        side=order_type,
        type='STOP_LOSS_LIMIT',
        quantity=quantity,
        price=price,
        stopPrice=price,
        timeInForce='GTC')



def check_cash(trading_client, coin, stored_cash):
    # extract the relevant prices
    current_btc_price = PRICE_LIST['BTCUSDT']
    current_price_in_btc= PRICE_LIST[coin+'BTC']
    current_price_in_usd = (current_price_in_btc*current_btc_price)

    #
    balance = trading_client.get_asset_balance(asset=coin)
    coin_available = float(balance['free'])+float(balance['locked'])
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

    print('POSITION: '+position)

    # perform the actual sell/buy options
    if position == 'buy':
        buy_all(trading_client=trading_client, coin=coin, cash_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all(trading_client=trading_client, coin=coin)*current_price

    # save the new bot status dict
    binance_bot_status[coin] = current_bot_status


    if position=='update_stoploss_sell':
        if coin+'USDT' in PRICE_LIST.keys():
            #CANCEL ALL ORDERS FOR THIS COIN FIRST
            balance = trading_client.get_asset_balance(asset=coin)
            coin_available = float(balance['free'])
            trading_client.create_order(
                symbol=coin+'USDT',
                side='SELL',
                type='STOP_LOSS_LIMIT',
                quantity=coin_available,
                price=current_bot_status['stoploss_price'],
                stopPrice=current_bot_status['stoploss_price'],
                timeInForce='GTC')
        else:
            print('Create stoploss sell order of {} at {}'.format(coin, current_bot_status['stoploss_price']))

    elif position=='update_stoploss_buy':
        if coin+'USDT' in PRICE_LIST.keys():
            trading_client.create_order(
                symbol=coin+'USDT',
                side='BUY',
                type='STOP_LOSS_LIMIT',
                quantity=current_bot_status['cash']/current_bot_status['stoploss_price'],
                price=current_bot_status['stoploss_price'],
                stopPrice=current_bot_status['stoploss_price'],
                timeInForce='GTC')
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
    PRICE_LIST = {}
    for pair in client.get_all_tickers():
        PRICE_LIST[pair['symbol']] = float(pair['price'])
    pprint(PRICE_LIST)
    # pprint(client.get_all_tickers())