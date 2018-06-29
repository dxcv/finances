from strategy_dynamic_stoploss import dynamic_stoploss_bitstamp_bot

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client = bts.Trading(
   username='769101',
   key='oHBLylRtmUfRY2A9JLeKOeIGAaKHmnvj',
   secret='u4eBOyegwk5VJLHqwlEaOjULUebOT9Yk'
   )


# BITCOIN
dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin='btc',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
    current_price=float(trading_client.ticker(base='btc', quote='eur')['last']),
    pct_gap=0.03,
    minimum_gain=0.01,
    reinvest_gap=0.5
    )

# ETHEREUM
dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin='eth',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
    current_price=float(trading_client.ticker(base='eth', quote='eur')['last']),
    pct_gap=0.03,
    minimum_gain=0.01,
    reinvest_gap=0.5
    )

# LITECOIN
dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin='ltc',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
    current_price=float(trading_client.ticker(base='ltc', quote='eur')['last']),
    pct_gap=0.03,
    minimum_gain=0.01,
    reinvest_gap=0.5
    )

# RIPLLE
dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin='xrp',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
    current_price=float(trading_client.ticker(base='xrp', quote='eur')['last']),
    pct_gap=0.03,
    minimum_gain=0.01,
    reinvest_gap=0.5
    )

# BITCOIN CASH
dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin='bch',
    bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
    current_price=float(trading_client.ticker(base='bch', quote='eur')['last']),
    pct_gap=0.03,
    minimum_gain=0.01,
    reinvest_gap=0.5
    )