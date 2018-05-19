from strategy_dynamic_stoploss import dynamic_stoploss_strategy

import bitstamp.client as bts
import os


cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_bch = bts.Trading(
   username='769101',
   key='Z1ZzxqDqXvLo1MmxRUhfdviqPtFrOCSx',
   secret='OyZ67LZXFqu3UYQDVY0qlMuO9suVUIGi'
   )

# to be run every 8H
dynamic_stoploss_strategy(
trading_client_bch,
coin='bch',
bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bch.json'),
current_price=float(trading_client_bch.ticker(base='bch', quote='eur')['last']),
pct_gap=0.06,
minimum_gain=0.09,
reinvest_gap=0.5
)
