import json

def buy_all(trading_client, coin):
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    eur_available = float(trading_client.account_balance(base=coin, quote="eur")['eur_available'])
    amount_to_buy = round(eur_available/current_price, 6)

    bought=False
    while not bought and amount_to_buy>0:
        try:
            trading_client.buy_market_order(amount=amount_to_buy, base=coin, quote="eur")
            bought=True
            print('Bought {0} {1} at {2} eur'.format(amount_to_buy, coin, current_price))
        except:
            amount_to_buy=round(0.9975*amount_to_buy,6)

def sell_all(trading_client, coin):
    coin_amount = float(trading_client.account_balance(base=coin, quote="eur")['{}_available'.format(coin)])
    amount_to_sell = round(coin_amount, 6)

    sold=False
    while not sold and amount_to_sell>0:
        try:
            trading_client.sell_market_order(amount=amount_to_sell, base=coin, quote="eur")
            sold=True
            print('Sold {0} {1} at {2} eur'.format(amount_to_sell, coin, current_price))
        except:
            amount_to_sell=round(amount_to_sell*0.9975, 6)

def decision_short(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision = 'hold'

    if current_price > top_price:
        decision = 'buy'

    elif current_price < bot_price:
        bot_price = current_price

    elif current_price > (reference_price-abs((reference_price-bot_price))*0.5) and current_price < reference_price*(1 - minimum_gain):
        decision = 'buy'

    return decision, top_price, bot_price


def decision_long(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision='hold'

    if current_price<bot_price:
        decision='sell'

    elif current_price>top_price:
        top_price=current_price

    elif current_price<(reference_price+abs((reference_price-top_price))*0.5) and current_price>reference_price*(1+minimum_gain):
        decision='sell'

    return decision, top_price, bot_price


def dynamic_stoploss_strategy(
    trading_client,
    bot_status_json_path,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):


    with open(bot_status_json_path) as json_file:
        current_bot_status = json.load(json_file)

    reference_price = current_bot_status['reference_price']
    top_price = current_bot_status['top_price']
    bot_price = current_bot_status['bot_price']

    cash = float(trading_client.account_balance(base='btc', quote="eur")['eur_available'])

    if cash < 5:  # less than 5 euro
        decision_strategy = decision_long
    else:
        decision_strategy = decision_short


    position, top_price, bot_price = decision_strategy(
        current_price=current_price,
        minimum_gain=minimum_gain,
        reference_price=current_bot_status['reference_price'],
        top_price=current_bot_status['top_price'],
        bot_price=current_bot_status['bot_price'],
        )
    print('Current position: {}'.format(position))

    if position == 'buy':
        buy_all(trading_client=trading_client, coin='btc')
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif position == 'sell':
        sell_all(trading_client=trading_client, coin='btc')
        reference_price = current_price
        bot_price = reference_price*(1-minimum_gain)
        top_price = reference_price*(1+pct_gap)

    # reinvest?
    elif current_price > reference_price*(1+reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif current_price < reference_price*(1-reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1+pct_gap)
        top_price = reference_price*(1-minimum_gain)

    current_bot_status['reference_price'] = reference_price
    current_bot_status['top_price'] = top_price
    current_bot_status['bot_price'] = bot_price

    bot_status_file = bot_status_json_path

    with open(bot_status_file, 'w') as f:
        json.dump(current_bot_status, f)

if __name__=='__main__':
    import bitstamp.client as bts
    import os

    cfd, cfn = os.path.split(os.path.abspath(__file__))

    trading_client = bts.Trading(
       username='769101',
       key='9JShgcZgw3rlDvcCGVh4mi9QodcPZy82',
       secret='GRKx4bOkKhDJh4Xex8eC3DtFK3MJwaO1'
       )
