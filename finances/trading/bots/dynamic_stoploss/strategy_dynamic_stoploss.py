import json

from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy

def buy_all(trading_client, coin, eur_quantity):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    eur_available = eur_quantity
    amount_to_buy = eur_available/current_price

    bought=False
    while not bought and amount_to_buy>0:
        try:
            trading_client.buy_market_order(amount=round(amount_to_buy,6), base=coin, quote="eur")
            bought=True
            print('Bought {0} {1} at {2} eur'.format(amount_to_buy, coin, current_price))
        except:
            amount_to_buy=0.9975*amount_to_buy

def sell_all(trading_client, coin):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    coin_available = float(trading_client.account_balance(base=coin, quote="eur")['{}_available'.format(coin)])
    amount_to_sell = coin_available

    sold=False
    while not sold and amount_to_sell>0:
        try:
            trading_client.sell_market_order(amount=round(amount_to_sell,6), base=coin, quote="eur")
            sold=True
            print('Sold {0} {1} at {2} eur'.format(amount_to_sell, coin, current_price))
        except:
            amount_to_sell=amount_to_sell*0.9975

    return amount_to_sell


def dynamic_stoploss_bitstamp_bot(
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
        buy_all(trading_client=trading_client, coin=coin, eur_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all(trading_client=trading_client, coin=coin)*current_price

    # save the new bot status dict
    binance_bot_status[coin] = current_bot_status

    with open(bot_status_json_path, 'w') as f:
        json.dump(binance_bot_status, f)

if __name__=='__main__':
    import bitstamp.client as bts
    import os

    cfd, cfn = os.path.split(os.path.abspath(__file__))

    trading_client = bts.Trading(
       username='769101',
       key='9JShgcZgw3rlDvcCGVh4mi9QodcPZy82',
       secret='GRKx4bOkKhDJh4Xex8eC3DtFK3MJwaO1'
       )
