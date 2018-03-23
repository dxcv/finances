import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client = bts.Trading(
   username='769101',
   key='9JShgcZgw3rlDvcCGVh4mi9QodcPZy82',
   secret='GRKx4bOkKhDJh4Xex8eC3DtFK3MJwaO1'
   )

dynamic_stoploss_strategy(
trading_client,
coin='eth',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_eth.json'),
current_price=float(trading_client.ticker(base='eth', quote='eur')['last']),
pct_gap=0.035,
minimum_gain=0.0475,
reinvest_gap=0.35
)