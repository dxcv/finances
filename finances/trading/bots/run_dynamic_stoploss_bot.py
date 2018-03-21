import json

from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client = bts.Trading(
   username='769101',
   key='mXt0zCJOzL49pGEw25uLneM5gqQ5weL4',
   secret='UmBn6XJ28s4Dz7EyjDYd6Fq3aFm9X7uj'
   )

dynamic_stoploss_strategy(
trading_client,
bot_status_json_path=os.path.join(cfd, 'trade_bot_status.json'),
current_price=float(trading_client.ticker(base='btc', quote='eur')['last']),
pct_gap=0.035,
minimum_gain=0.025,
reinvest_gap=0.35
)