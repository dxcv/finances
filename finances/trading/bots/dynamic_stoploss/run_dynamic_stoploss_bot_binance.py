import json

from strategy_dynamic_stoploss_binance import dynamic_stoploss_binance_bot#, sell_all, buy_all
from binance.client import Client

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_binance = Client(
    api_key='69SJ6W75YXxMqeM2uOHsYPidRHHc1tDuVa723QjcP7p8xKQOCvqi80QnoYoWFqdM',
    api_secret='6n3h0d7FvGiWTjF8Tm3NskURNpa2NnXbmqQfDinwOV0buPzE2W4aFDefkxpkgSco'
    )

price_list={}
for pair in trading_client_binance.get_all_tickers():
    price_list[pair['symbol']] = float(pair['price'])

btc_price = price_list['BTCUSDT']


# def create_dict(coins):
#     d = {}
#     for coin in coins:
#         current_btc_price = price_list['BTCUSDT']
#         current_price_in_btc= price_list[coin+'BTC']
#         current_price_in_usd = (current_price_in_btc*current_btc_price)

#         d[coin] = {
#             "reference_price": current_price_in_usd,
#             "top_price": current_price_in_usd*1.09,
#             "bot_price": current_price_in_usd*0.91,
#             "cash": 0}

#     return d

# from pprint import pprint
# print(create_dict(['XLM', 'TRX', 'ADA', 'IOTA', 'EOS']))

# STELLAR
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='XLM',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['XLMBTC']*btc_price,
    pct_gap=0.09,
    minimum_gain=0.09,
    reinvest_gap=0.5
)


# CARDANO
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='ADA',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['ADABTC']*btc_price,
    pct_gap=0.09,
    minimum_gain=0.09,
    reinvest_gap=0.5
)

# TRON
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='TRX',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['TRXBTC']*btc_price,
    pct_gap=0.09,
    minimum_gain=0.09,
    reinvest_gap=0.5
)

# EOS
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='EOS',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['EOSBTC']*btc_price,
    pct_gap=0.09,
    minimum_gain=0.09,
    reinvest_gap=0.5
)