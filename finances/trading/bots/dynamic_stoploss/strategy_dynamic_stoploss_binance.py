import json

from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy

def buy_all_with_btc(trading_client, coin, btc_quantity):
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])
    current_price= price_list[coin+'BTC']
    amount_to_buy = btc_quantity/current_price

    bought=False
    while not bought and amount_to_buy>0:
        try:
            trading_client.order_market_buy(
                symbol=coin+'BTC',
                quantity=int(amount_to_buy)
            )
            bought=True
            print('Bought {0} {1}'.format(amount_to_buy, coin))
        except:
            amount_to_buy=0.9975*amount_to_buy


def sell_all_for_btc(trading_client, coin):
    coin_available = float(trading_client.get_asset_balance(asset=coin)['free'])
    amount_to_sell = coin_available
    print(amount_to_sell)

    sold=False
    while not sold and amount_to_sell>0:
        try:
            trading_client.order_market_sell(
                symbol=coin+'BTC',
                quantity=amount_to_sell
            )
            sold=True
            print('Sold {0} {1}'.format(amount_to_sell, coin))
        except:
            amount_to_sell=amount_to_sell*0.9975
    return amount_to_sell


def dynamic_stoploss_binance_bot(
    trading_client,
    coin,
    bot_status_json_path,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.8
    ):

    with open(bot_status_json_path) as json_file:
        binance_bot_status = json.load(json_file)

    current_bot_status = binance_bot_status[coin]

    current_bot_status, position = dynamic_stoploss_strategy(
        status_dict=current_bot_status,
        cash=current_bot_status['cash'],
        current_price=current_price,
        pct_gap=pct_gap,
        minimum_gain=minimum_gain,
        reinvest_gap=reinvest_gap
        )

    # perform the actual sell/buy options
    if position == 'buy':
        buy_all_with_btc(trading_client=trading_client, coin=coin, btc_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all_for_btc(trading_client=trading_client, coin=coin)*current_price

    # save the new bot status dict
    binance_bot_status[coin] = current_bot_status

    with open(bot_status_json_path, 'w') as f:
        json.dump(binance_bot_status, f)

if __name__=='__main__':
    from binance.client import Client
    from pprint import pprint

    api_key='QuJSzBd0O8Uube4sOr1DOySMsZWsKC5EpjFYP12FZPO0WEQbBrjjU8N5kVPb5Qkt'
    api_secret = 'XiPd9cc3VHDl5sa0juCYs27kVPipPEMkddmHxYol6pGuOWgLsZK4cH7SwpJf4Qev'
    client = Client(api_key, api_secret)
    all_tickers = client.get_all_tickers()
    price_list = {}
    for pair in client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])
    pprint(price_list)
    # pprint(client.get_all_tickers())