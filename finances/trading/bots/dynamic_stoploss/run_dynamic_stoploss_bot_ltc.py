import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client = bts.Trading(
   username='769101',
   key='1uy9vw6puPcy6tO7L1qs2EdSZGaPeROU',
   secret='5ofFS0z0wgUz44HqRXwnLDVCmzOEeBc1'
   )

# to be run every 4 hours
dynamic_stoploss_strategy(
trading_client,
coin='ltc',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_ltc.json'),
current_price=float(trading_client.ticker(base='ltc', quote='eur')['last']),
pct_gap=0.025,
minimum_gain=0.035,
reinvest_gap=0.35
)
