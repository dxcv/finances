from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_eth = bts.Trading(
   username='769101',
   key='xMVKpVIPy6rC6THS4nA3Mdmp9yhEc5jF',
   secret='h7owGh2AV7cuci2ftXSqu006bUWk5fnF'
   )

# to be run every 4 hours
dynamic_stoploss_strategy(
trading_client_eth,
coin='eth',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_eth.json'),
current_price=float(trading_client_eth.ticker(base='eth', quote='eur')['last']),
pct_gap=0.03,
minimum_gain=0.03,
reinvest_gap=0.5
)