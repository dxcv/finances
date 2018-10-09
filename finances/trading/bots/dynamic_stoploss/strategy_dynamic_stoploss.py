import json
import os
import sys

cfp, cfn = os.path.split(os.path.abspath(__file__))

sys.path.append(os.path.join(cfp, '..', '..', '..', '..'))   # <--------- this is to run in pythonanywhere

from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import dynamic_stoploss_strategy

def buy_all(trading_client, cash_quantity, coin='btc'):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    eur_available = cash_quantity
    amount_to_buy = eur_available/current_price

    bought=False
    counter=0
    while not bought and amount_to_buy>0 and counter < 20:
        try:
            trading_client.buy_market_order(amount=round(amount_to_buy,6), base=coin, quote="eur")
            bought=True
            print('Bought {0} {1} at {2} eur'.format(amount_to_buy, coin, current_price))
        except:
            counter+=1
            amount_to_buy=0.9975*amount_to_buy


def sell_all(trading_client, coin='btc'):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    coin_available = float(trading_client.account_balance(base=coin, quote="eur")['{}_available'.format(coin)])
    """
    Returns: the ammount of coin to be sold
    """
    amount_to_sell = coin_available

    sold=False
    counter = 0
    while not sold and amount_to_sell>0 and counter < 20:
        try:
            trading_client.sell_market_order(amount=round(amount_to_sell,6), base=coin, quote="eur")
            sold=True
            print('Sold {0} {1} at {2} eur'.format(amount_to_sell, coin, current_price))
        except:
            amount_to_sell=amount_to_sell*0.9975
            counter+=1

    return amount_to_sell

def check_cash(trading_client, coin, stored_cash):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    coin_available = float(trading_client.account_balance(base=coin, quote="eur")['{}_balance'.format(coin)])
    value = coin_available*current_price
    if value < 10:  # se o valor for inferior a 5€
        value = 0

    if stored_cash==0 and value == 0:
        # in this case, there was a stoploss sell transaction and we need to check for how much
        print('Sell stoploss detected')
        last_transaction=abs(float(trading_client.user_transactions(
                offset=0,
                limit=1,
                descending=True,
                base=coin,
                quote='eur')[0]['eur']))
        return last_transaction
    elif stored_cash>0 and value >0:
        print('Buy stoploss detected')
        # in this case, there was a stoploss buy transaction
        return 0
    else:
        return stored_cash



def dynamic_stoploss_bitstamp_bot(
    trading_client,
    coin,
    bot_status_json_path,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.5
    ):

    with open(bot_status_json_path) as json_file:
        bitstamp_bot_status = json.load(json_file)

    current_bot_status = bitstamp_bot_status[coin]

    current_bot_status['cash'] = check_cash(trading_client, coin, stored_cash=current_bot_status['cash'])

    current_bot_status, position = dynamic_stoploss_strategy(
        status_dict=current_bot_status,
        cash=current_bot_status['cash'],
        current_price=current_price,
        pct_gap=pct_gap,
        minimum_gain=minimum_gain,
        reinvest_gap=reinvest_gap
        )

    print('Position: '+position)

    # perform the actual sell/buy options
    if position == 'buy':
        buy_all(trading_client=trading_client, coin=coin, cash_quantity=current_bot_status['cash'])
        current_bot_status['cash'] = 0

    elif position == 'sell':
        current_bot_status['cash'] = sell_all(trading_client=trading_client, coin=coin)*current_price


    if position=='update_stoploss_sell':
        print('Create stoploss sell order of {} at {}'.format(coin, current_bot_status['stoploss_price']))

    elif position=='update_stoploss_buy':
        print('Create stoploss buy order of {} at {}'.format(coin, current_bot_status['stoploss_price']))

    # save the new bot status dict
    bitstamp_bot_status[coin] = current_bot_status

    with open(bot_status_json_path, 'w') as f:
        json.dump(bitstamp_bot_status, f, sort_keys=True, indent=4)

if __name__=='__main__':
    import bitstamp.client as bts
    import os

    cfd, cfn = os.path.split(os.path.abspath(__file__))

    trading_client = bts.Trading(
       username='769101',
       key='9JShgcZgw3rlDvcCGVh4mi9QodcPZy82',
       secret='GRKx4bOkKhDJh4Xex8eC3DtFK3MJwaO1'
       )
