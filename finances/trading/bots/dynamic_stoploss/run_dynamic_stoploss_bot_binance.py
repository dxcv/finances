import json

from strategy_dynamic_stoploss_binance import dynamic_stoploss_strategy
from binance.client import Client

import bitstamp.client as bts
import os

cfd, cfn = os.path.split(os.path.abspath(__file__))

trading_client_binance = Client(
	'QuJSzBd0O8Uube4sOr1DOySMsZWsKC5EpjFYP12FZPO0WEQbBrjjU8N5kVPb5Qkt',
	'XiPd9cc3VHDl5sa0juCYs27kVPipPEMkddmHxYol6pGuOWgLsZK4cH7SwpJf4Qev'
	)

price_list={}
for pair in trading_client_binance.get_all_tickers():
    price_list[pair['symbol']] = float(pair['price'])

# STELLAR
dynamic_stoploss_strategy(
	trading_client_binance,
	coin='XLM',
	bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
	current_price=price_list['XLMBTC'],
	pct_gap=0.09,
	minimum_gain=0.09,
	reinvest_gap=0.5
)


# CARDANO
dynamic_stoploss_strategy(
	trading_client_binance,
	coin='ADA',
	bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
	current_price=price_list['ADABTC'],
	pct_gap=0.09,
	minimum_gain=0.09,
	reinvest_gap=0.5
)

# TRON
dynamic_stoploss_strategy(
	trading_client_binance,
	coin='TRX',
	bot_status_json_path=os.path.join(cfd, 'trade_bot_status_binance.json'),
	current_price=price_list['TRXBTC'],
	pct_gap=0.09,
	minimum_gain=0.09,
	reinvest_gap=0.5
)