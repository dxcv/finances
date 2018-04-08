from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_btc = bts.Trading(
   username='769101',
   key='9JShgcZgw3rlDvcCGVh4mi9QodcPZy82',
   secret='GRKx4bOkKhDJh4Xex8eC3DtFK3MJwaO1'
   )

# to be run every 8 hours
dynamic_stoploss_strategy(
trading_client_btc,
coin='btc',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_btc.json'),
current_price=float(trading_client_btc.ticker(base='btc', quote='eur')['last']),
pct_gap=0.035,
minimum_gain=0.0125,
reinvest_gap=0.35
)