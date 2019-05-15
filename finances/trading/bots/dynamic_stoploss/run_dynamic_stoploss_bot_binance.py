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


# STELLAR
print('::: XLM :::')
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='XLM',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['XLMBTC']*btc_price,
    pct_gap=0.01,
    minimum_gain=0.01,
    reinvest_gap=0.5
)

# CARDANO
print('::: ADA :::')
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='ADA',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['ADABTC']*btc_price,
    pct_gap=0.01,
    minimum_gain=0.01,
    reinvest_gap=0.5
)

# TRON
print('::: TRX :::')
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='TRX',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['TRXBTC']*btc_price,
    pct_gap=0.03,
    minimum_gain=0.02,
    reinvest_gap=0.5
)

# IOTA
print('::: IOTA :::')
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='IOTA',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['IOTABTC']*btc_price,
    pct_gap=0.03,
    minimum_gain=0.02,
    reinvest_gap=0.5
)

# NEO
print('::: NEO :::')
dynamic_stoploss_binance_bot(
    trading_client_binance,
    coin='NEO',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
    current_price=price_list['NEOBTC']*btc_price,
    pct_gap=0.03,
    minimum_gain=0.02,
    reinvest_gap=0.5
)

# # XMR
# print('::: XMR :::')
# dynamic_stoploss_binance_bot(
#     trading_client_binance,
#     coin='XMR',
#     bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
#     current_price=price_list['XMRBTC']*btc_price,
#     pct_gap=0.01,
#     minimum_gain=0.01,
#     reinvest_gap=0.5
# )

# # DASH
# print('::: DASH :::')
# dynamic_stoploss_binance_bot(
#     trading_client_binance,
#     coin='DASH',
#     bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
#     current_price=price_list['DASHBTC']*btc_price,
#     pct_gap=0.01,
#     minimum_gain=0.01,
#     reinvest_gap=0.5
# )