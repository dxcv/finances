import json
import pandas as pd
# import matplotlib.pyplot as plt

def update_price_levels(price, bot_lvl, top_lvl):
    bot_price = price*(1-bot_lvl)
    top_price = price*(1+top_lvl)
    return price, bot_price, top_price
    

def decision_short(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price
    ):

    decision = 'hold'

    if current_price > top_price:
        decision = 'buy'
        return decision, top_price, bot_price, 0

    buy_price = reference_price+abs((reference_price-top_price))*0.5
    if current_price < bot_price:
        bot_price = current_price
        buy_price = reference_price+abs((reference_price-bot_price))*0.5
        decision='update_stoploss_buy'

    if buy_price > reference_price*(1-minimum_gain):
        decision='hold'
        buy_price=0

    return decision, top_price, bot_price, buy_price


def decision_long(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price
    ):

    decision='hold'

    if current_price<bot_price:
        decision='sell'
        return decision, top_price, bot_price, 0

    sell_price = reference_price+abs((reference_price-top_price))*0.5
    if current_price>top_price:
        top_price=current_price
        sell_price = reference_price+abs((reference_price-top_price))*0.5
        decision='update_stoploss_sell'

    if sell_price < reference_price*(1+minimum_gain):
        decision='hold'
        sell_price=0

    return decision, top_price, bot_price, sell_price


# NEED TO DEFINE THESE DECISIONS ABOVE

def dynamic_stoploss_strategy(
    status_dict,
    cash,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.35
    ):

    reference_price= status_dict['reference_price']
    top_price=status_dict['top_price']
    bot_price=status_dict['bot_price']
    stoploss_price=status_dict['stoploss_price']

    # first we need to check if there was a stoploss transaction:
    if cash == 0:
        decision_strategy = decision_long
        if stoploss_price < reference_price and stoploss_price>0:
            reference_price, bot_price, top_price = update_price_levels(stoploss_price, pct_gap, minimum_gain)

    else:
        decision_strategy = decision_short
        if stoploss_price > reference_price  and stoploss_price>0:
            reference_price, bot_price, top_price = update_price_levels(stoploss_price, minimum_gain, pct_gap)

    position, top_price, bot_price, stoploss_price = decision_strategy(
        minimum_gain=minimum_gain,
        current_price=current_price,
        reference_price=reference_price,
        top_price=top_price,
        bot_price=bot_price,
        )

    if position == 'buy':
        reference_price, bot_price, top_price = update_price_levels(current_price, pct_gap, minimum_gain)

    elif position == 'sell':
        reference_price, bot_price, top_price = update_price_levels(current_price, minimum_gain, pct_gap)

    # reinvest?
    elif current_price > reference_price*(1+reinvest_gap):
        reference_price, bot_price, top_price = update_price_levels(current_price, pct_gap, minimum_gain)

    elif current_price < reference_price*(1-reinvest_gap):
        reference_price, bot_price, top_price = update_price_levels(current_price, minimum_gain, pct_gap)

    status_dict['reference_price'] = reference_price
    status_dict['top_price'] = top_price
    status_dict['bot_price'] = bot_price
    status_dict['stoploss_price'] = stoploss_price

    return status_dict, position


def run_dynamic_stoploss_strategy(
    price_series,
    pct_gap=0.03,
    minimum_gain=0.01,
    fee=0.0025,
    invested_value=100,
    debug=False):

    # set initial positions
    coin_amount = invested_value/price_series.iloc[0]
    current_cash = 0
    position = 'hold'

    status_dict={}
    status_dict['reference_price']=price_series.iloc[0]
    status_dict['bot_price']=price_series.iloc[0]*(1-pct_gap)
    status_dict['top_price']=price_series.iloc[0]*(1+minimum_gain)
    status_dict['stoploss_price']=0

    trading_value = [invested_value]
    for k in range(1,len(price_series)):
        date = price_series.index[k]
        current_price = price_series.loc[date]

        if debug:
            fig, ax = plt.subplots(2,1, sharex=True)
            ax[0].plot(price_series.index[:k], price_series.values[:k], '-o')
            ax[1].plot(price_series.index[:k], trading_value[:k], '-o')
            print(status_dict)
            print('cash: {}'.format(current_cash))


        if current_cash >0  and current_price>status_dict['stoploss_price'] and status_dict['stoploss_price']>0:
            price=status_dict['stoploss_price']
            coin_amount = current_cash/(price)*(1-fee)
            current_cash=0
        elif current_cash == 0  and current_price<status_dict['stoploss_price'] and status_dict['stoploss_price']>0:
            price=status_dict['stoploss_price']
            current_cash = coin_amount*price*(1-fee)
            coin_amount = 0

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

        if debug:
            print('Current Price: {}'.format(current_price))
            print('Position: {}'.format(position))
            print('------')
            plt.show()

        value = coin_amount*current_price+current_cash
        trading_value.append(value)


    return pd.Series(data=trading_value, index=price_series.index)