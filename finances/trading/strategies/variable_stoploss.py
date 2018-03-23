import pandas as pd
import datetime
import pickle
import os
import numpy as np
import random
from finances.market import market_data as mkt_data

cfd, cfn = os.path.split(os.path.abspath(__file__))

def decision_short(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision='hold'

    if current_price>top_price:
        decision='buy'

    elif current_price<bot_price:
        bot_price=current_price

    elif current_price>(reference_price-abs((reference_price-bot_price))*0.5) and current_price<reference_price*(1-minimum_gain):
        decision='buy'

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


def asymmetric_decision(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    cash,
    coin_amount,
    fee=0.0025):

    if cash==0:
        decision_strategy = decision_long
    else:
        decision_strategy = decision_short

    position, top_price, bot_price = decision_strategy(
        minimum_gain,
        reference_price,
        current_price,
        top_price,
        bot_price,
        )

    return position, top_price, bot_price


def dynamic_stoploss_strategy(
    price_series,
    pct_gap,
    minimum_gain=2*0.0025,
    fee=0.0025,
    invested_value=100):

    coin_amount = invested_value/price_series.iloc[0]
    cash = 0
    position = 'hold'

    trading_value = [invested_value]

    reference_price = price_series.iloc[0]
    bot_price=reference_price*(1-pct_gap)
    top_price=reference_price*(1+2*fee)

    sell_points = {'index':[], 'data':[]}
    buy_points = {'index':[], 'data':[]}

    for k in range(1,len(price_series)):
        date = price_series.index[k]
        # print(date)

        current_price = price_series.loc[date]

        position, top_price, bot_price = asymmetric_decision(
            minimum_gain,
            reference_price,
            current_price,
            top_price,
            bot_price,
            cash,
            coin_amount,
            fee
            )

        # # for debugg
        # price_series.iloc[:k+1].plot(style='-o')
        # if len(buy_points['index'])>0:
        #     plt.plot(buy_points['index'], buy_points['data'])

        # print('POSITION', position)
        # print('current', current_price)
        # print('reference', reference_price)
        # print('TOP', top_price)
        # print('BOT', bot_price)
        # print('########################################')
        # plt.show()

        if position == 'buy':
            coin_amount = cash/(current_price)*(1-fee)
            cash = 0
            reference_price=current_price
            bot_price=reference_price*(1-pct_gap)
            top_price=reference_price*(1+2*fee)

            buy_points['index'].append(date)
            buy_points['data'].append(current_price)

        elif position == 'sell':
            cash = coin_amount*current_price*(1-fee)
            coin_amount = 0
            reference_price=current_price
            bot_price=reference_price*(1-2*fee)
            top_price=reference_price*(1+pct_gap)

            sell_points['index'].append(date)
            sell_points['data'].append(current_price)

        else:
            if current_price > reference_price*(1+0.35):
                reference_price=current_price
                bot_price=reference_price*(1-pct_gap)
                top_price=reference_price*(1+2*fee)

            elif current_price < reference_price*(1-0.35):
                reference_price=current_price
                bot_price=reference_price*(1+pct_gap)
                top_price=reference_price*(1-2*fee)
        value = coin_amount*current_price+cash
        trading_value.append(value)


    buy_data = pd.Series(index=buy_points['index'], data=buy_points['data'])
    sell_data = pd.Series(index=sell_points['index'], data=sell_points['data'])
    return pd.Series(data=trading_value, index=price_series.index)#, buy_data, sell_data



if __name__=='__main__':

    pct_gap = 0.035
    top_price=0
    bot_price=0
    min_gain=0.025

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['BTC'].loc[datetime.datetime(2018,1,26):].resample('8H').last()

    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*100.0/price_data.iloc[0]

    strategy_result, buy, sell = dynamic_stoploss_strategy(pct_gap=pct_gap, price_series=price_data, minimum_gain=min_gain)

    backtest_df['strategy'] = strategy_result

    fig, ax = plt.subplots(2,1, sharex=True)
    backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    price_data.plot(ax=ax[1])
    buy.plot(ax=ax[1], style='go')
    sell.plot(ax=ax[1], style='rx')

    plt.show()
