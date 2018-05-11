from binance.client import Client
from pprint import pprint

api_key='QuJSzBd0O8Uube4sOr1DOySMsZWsKC5EpjFYP12FZPO0WEQbBrjjU8N5kVPb5Qkt'
api_secret = 'XiPd9cc3VHDl5sa0juCYs27kVPipPEMkddmHxYol6pGuOWgLsZK4cH7SwpJf4Qev'
client = Client(api_key, api_secret)

prices = client.get_all_tickers()

# pprint(prices)

klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

from binance.exceptions import BinanceAPIException, BinanceWithdrawException
try:
    order = client.order_limit_sell(
        symbol='BNBBTlC',
        quantity=100,
        price='0.00001')
except BinanceAPIException as e:
    print(e)
except BinanceWithdrawException as e:
    print(e)
else:
    print("Success")
