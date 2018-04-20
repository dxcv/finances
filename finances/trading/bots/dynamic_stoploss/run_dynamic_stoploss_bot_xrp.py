import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_xrp = bts.Trading(
   username='769101',
   key='fifYuo3MdXR98eAEGci844fFbBCcoTdn',
   secret='yET9TpIOllV8MwR0qHFMp5vgFjVSwTbn'
   )

# to be run in 8h periods
dynamic_stoploss_strategy(
trading_client_xrp,
coin='xrp',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_xrp.json'),
current_price=float(trading_client_xrp.ticker(base='xrp', quote='eur')['last']),
pct_gap=0.035,
minimum_gain=0.0175,
reinvest_gap=0.35
)
