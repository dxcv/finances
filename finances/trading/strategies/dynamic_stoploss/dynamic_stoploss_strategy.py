import json
import pandas as pd

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
    current_price = float(trading_client.ticker(base=coin, quote='eur')['last'])
    coin_available = float(trading_client.account_balance(base=coin, quote="eur")['{}_available'.format(coin)])
    amount_to_sell = round(coin_available, 6)

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


###
    with open(bot_status_json_path) as json_file:
        current_bot_status = json.load(json_file)

    reference_price = current_bot_status['reference_price']
    top_price = current_bot_status['top_price']
    bot_price = current_bot_status['bot_price']

    cash = float(trading_client.account_balance(base=coin, quote="eur")['eur_available'])


def dynamic_stoploss_strategy(
    status_dict,
    cash,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):

    if cash < 5:  # less than 5 euro
        decision_strategy = decision_long
    else:
        decision_strategy = decision_short

    reference_price= status_dict['reference_price']
    top_price=status_dict['top_price']
    bot_price=status_dict['bot_price']

    position, top_price, bot_price = decision_strategy(
        current_price=current_price,
        minimum_gain=minimum_gain,
        reference_price=reference_price,
        top_price=top_price,
        bot_price=bot_price,
        )

    if position == 'buy':
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif position == 'sell':
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

    status_dict['reference_price'] = reference_price
    status_dict['top_price'] = top_price
    status_dict['bot_price'] = bot_price

    return status_dict, position


def run_dynamic_stoploss_strategy(
    price_series,
    pct_gap=0.035,
    minimum_gain=0.0175,
    fee=0.0025,
    invested_value=100):

    # set initial positions
    coin_amount = invested_value/price_series.iloc[0]
    current_cash = 0
    position = 'hold'

    status_dict={}
    status_dict['reference_price']=price_series.iloc[0]
    status_dict['top_price']=price_series.iloc[0]*(1-pct_gap)
    status_dict['bot_price']=price_series.iloc[0]*(1+minimum_gain)

    trading_value = [invested_value]
    for k in range(1,len(price_series)):
        date = price_series.index[k]
        current_price = price_series.loc[date]

        status_dict, position = dynamic_stoploss_strategy(
            status_dict=status_dict,
            cash=current_cash,
            current_price=current_price,
            pct_gap=pct_gap,
            minimum_gain=minimum_gain,
            reinvest_gap=0.5
            )

        if position == 'buy':
            coin_amount = current_cash/(current_price)*(1-fee)
            current_cash = 0

        elif position == 'sell':
            current_cash = coin_amount*current_price*(1-fee)
            coin_amount = 0

        value = coin_amount*current_price+current_cash
        trading_value.append(value)

    return pd.Series(data=trading_value, index=price_series.index)