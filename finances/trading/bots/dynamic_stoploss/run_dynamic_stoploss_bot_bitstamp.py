from strategy_dynamic_stoploss import dynamic_stoploss_bitstamp_bot

import bitstamp.client as bts
import os
import time

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client = bts.Trading(
   username='769101',
   key='DN0WD4ezCXTPZpdyKOBXnWukwOxoYwES',
   secret='TSQa4EBHzerJPwPpzDvdLP8CsN8cY4bC'
   )

failed_times = 0

while failed_times<3:
    try:
        print('---------- BTC bot:')
        # BITCOIN
        dynamic_stoploss_bitstamp_bot(
            trading_client,
            coin='btc',
            bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
            current_price=float(trading_client.ticker(base='btc', quote='eur')['last']),
            pct_gap=0.05,
            minimum_gain=0.01,
            reinvest_gap=0.5
            )

        print('---------- ETH bot:')
        # ETHEREUM
        dynamic_stoploss_bitstamp_bot(
            trading_client,
            coin='eth',
            bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
            current_price=float(trading_client.ticker(base='eth', quote='eur')['last']),
            pct_gap=0.01,
            minimum_gain=0.01,
            reinvest_gap=0.5
            )

        print('---------- LTC bot:')
        # LITECOIN
        dynamic_stoploss_bitstamp_bot(
            trading_client,
            coin='ltc',
            bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
            current_price=float(trading_client.ticker(base='ltc', quote='eur')['last']),
            pct_gap=0.01,
            minimum_gain=0.01,
            reinvest_gap=0.5
            )

        print('---------- XRP bot:')
        # RIPPLE
        dynamic_stoploss_bitstamp_bot(
            trading_client,
            coin='xrp',
            bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
            current_price=float(trading_client.ticker(base='xrp', quote='eur')['last']),
            pct_gap=0.01,
            minimum_gain=0.01,
            reinvest_gap=0.5
            )

        print('---------- BCH bot:')
        # BITCOIN CASH
        dynamic_stoploss_bitstamp_bot(
            trading_client,
            coin='bch',
            bot_status_json_path=os.path.join(cfd, 'trade_bot_status_bitstamp.json'),
            current_price=float(trading_client.ticker(base='bch', quote='eur')['last']),
            pct_gap=0.01,
            minimum_gain=0.01,
            reinvest_gap=0.5
            )

        failed_times = 5

    except bts.BitstampError as e:
        print('Failed: {} | Repeating!'.format(e))
        failed_times +=1
        time.sleep(15)
