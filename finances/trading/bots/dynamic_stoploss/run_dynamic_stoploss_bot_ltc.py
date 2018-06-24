import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_ltc = bts.Trading(
   username='769101',
   key='iZ8sb18cfTdArsP57avbIe8kqTNbwb8W',
   secret='4MbSn5SYhU5ggW0JgsqX1UPaTTOLzFgb'
   )

# to be run every 4 hours
dynamic_stoploss_strategy(
trading_client_ltc,
coin='ltc',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_ltc.json'),
current_price=float(trading_client_ltc.ticker(base='ltc', quote='eur')['last']),
pct_gap=0.01,
minimum_gain=0.04,
reinvest_gap=0.5
)
