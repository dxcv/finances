import json
import time

from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy
from binance.exceptions import BinanceAPIException

def buy_all(trading_client, coin, usd_quantity):

    # get all the prices
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])

    # extract the relevant prices
    current_btc_price = price_list['BTCUSDT']
    current_price_in_btc= price_list[coin+'BTC']
    current_price_in_usd = (current_price_in_btc*current_btc_price)

    # calculate the amount of both coin and btc to buy
    amount_to_buy = usd_quantity/current_price_in_usd
    btc_to_buy = usd_quantity/current_btc_price

    bought_btc=False
    bought_coin=False

    # first buy the corresponding amount of btc
    while not bought_btc and btc_to_buy>0:
        try:
            trading_client.order_market_buy(
                symbol='BTCUSDT',
                quantity=round(btc_to_buy, 5)
            )
            bought_btc=True
            print('Bought {0} BTC'.format(btc_to_buy))
        except BinanceAPIException as e:
            btc_to_buy*=0.9975

    # then buy the corresponding amount of the required coin
    time.sleep(2)  # wait a bit for the previous transaction take place
    rounder=5
    
    while not bought_coin and amount_to_buy>0.0:
        try:
            trading_client.order_market_buy(
                symbol=coin+'BTC',
                quantity=round(amount_to_buy, rounder)
            )
            bought_coin=True
            print('Bought {0} {1}'.format(amount_to_buy, coin))
        except BinanceAPIException as e:
            if 'LOT_SIZE' in str(e):
                rounder -=1
            if 'insufficient balance' in str(e):
                amount_to_buy*=0.9975


def sell_all(trading_client, coin):
    coin_available = float(trading_client.get_asset_balance(asset=coin)['free'])
    amount_to_sell = coin_available

    sold_coin=False
    rounder = 5
    sold_btc=False

    # first sell all to btc
    while not sold_coin and amount_to_sell>0:
        try:
            trading_client.order_market_sell(
                symbol=coin+'BTC',
                quantity=round(amount_to_sell, rounder)
            )
            sold_coin=True
            print('Sold {0} {1}'.format(amount_to_sell, coin))
        except BinanceAPIException as e:
            if 'LOT_SIZE' in str(e):
                rounder -=1
            if 'insufficient balance' in str(e):
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
            print('Sold {0} BTC'.format(btc_to_sell))
        except BinanceAPIException as e:
            btc_to_sell=btc_to_sell*0.9975

    return amount_to_sell


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

    current_bot_status, position = dynamic_stoploss_strategy(
        status_dict=current_bot_status,
        cash=current_bot_status['cash'],
        current_price=current_price,
        pct_gap=pct_gap,
        minimum_gain=minimum_gain,
        reinvest_gap=reinvest_gap
        )

    # perform the actual sell/buy options
    if position == 'buy':
        buy_all(trading_client=trading_client, coin=coin, btc_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all(trading_client=trading_client, coin=coin)*current_price

    # save the new bot status dict
    binance_bot_status[coin] = current_bot_status

    with open(bot_status_json_path, 'w') as f:
        json.dump(binance_bot_status, f)

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