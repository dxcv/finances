import json
import pandas as pd

def decision_short(
    reference_price,
    current_price,
    top_price,
    bot_price
    ):

    decision = 'hold'

    if current_price > top_price:
        decision = 'buy'

    elif current_price < bot_price:
        bot_price = current_price
        stoploss_price = (reference_price-abs((reference_price-bot_price))*0.5)
        decision='update_stoploss_buy'

    return decision, top_price, bot_price, stoploss_price


def decision_long(
    reference_price,
    current_price,
    top_price,
    bot_price
    ):

    decision='hold'

    if current_price<bot_price:
        decision='sell'

    elif current_price>top_price:
        stoploss_price = reference_price+abs((reference_price-top_price))*0.5
        top_price=current_price
        decision='update_stoploss_sell'

    return decision, top_price, bot_price, stoploss_price


def dynamic_stoploss_strategy(
    status_dict,
    cash,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):

    if cash == 0:
        decision_strategy = decision_long
    else:
        decision_strategy = decision_short

    reference_price= status_dict['reference_price']
    top_price=status_dict['top_price']
    bot_price=status_dict['bot_price']
    stoploss_price_old=status_dict['stoploss_price']

    position, top_price, bot_price, stoploss_price = decision_strategy(
        current_price=current_price,
        reference_price=reference_price,
        top_price=top_price,
        bot_price=bot_price,
        )

    if position=='update_stoploss_sell':
        print('Create stoploss sell order at'.format(stoploss_price))
    elif position=='update_stoploss_buy':
        print('Create stoploss buy order at'.format(stoploss_price))

    elif position == 'buy':
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