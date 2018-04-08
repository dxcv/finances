from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_eth = bts.Trading(
   username='769101',
   key='owkttzabH1Lph5qfLeelvt1dK6DXlXAe',
   secret='k34gpVPH1taeVWFkvRZdiWvROjfifmx7'
   )

# to be run every 4 hours
dynamic_stoploss_strategy(
trading_client_eth,
coin='eth',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_eth.json'),
current_price=float(trading_client_eth.ticker(base='eth', quote='eur')['last']),
pct_gap=0.035,
minimum_gain=0.0175,
reinvest_gap=0.35
)