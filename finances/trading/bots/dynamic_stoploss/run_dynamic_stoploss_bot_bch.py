import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_bch = bts.Trading(
   username='769101',
   key='aU1G6LJFKvRi5Cz4iVAvDliLlUqVMFZc',
   secret='IStHGikXR6owqWnwi0xHqUvdB9yKBa2g'
   )


# to be run every 8H
dynamic_stoploss_strategy(
trading_client_bch,
coin='bch',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bch.json'),
current_price=float(trading_client_bch.ticker(base='bch', quote='eur')['last']),
pct_gap=0.025,
minimum_gain=0.03,
reinvest_gap=0.35
)