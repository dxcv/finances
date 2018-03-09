import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt
import random
from finances.market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))

pct_gap = 0.01

def decision_short(
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

    elif current_price>(reference_price+bot_price)*0.5 and current_price<reference_price*(1-0.025):
        decision='buy'

    return decision


def decision_long(
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision='hold'

    print('current', current_price)
    print('reference', bot_price)
    
    if current_price<bot_price:
        decision='sell'

    elif current_price>top_price:
        top_price=current_price

    elif current_price<(reference_price+top_price)*0.5 and current_price>reference_price*(1+0.025):
            decision='sell'
    print(decision)

    return decision


def asymmetric_decision(
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

    position = decision_strategy(
        reference_price,
        current_price,
        top_price,
        bot_price,
        )
    print('position', position)
    
    return position


def adv_stop_loss_strategy(
    price_series,
    pct_gap=pct_gap,
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

        current_price = price_series.loc[date]

        print(price_series.iloc[:k])
        plt.plot(price_series.index[:k], price_series.iloc[:k], '-o')
        if len(buy_points['index'])>0:
            plt.plot(buy_points['index'], buy_points['data'])
        plt.show()

        position = asymmetric_decision(
            reference_price,
            current_price,
            top_price,
            bot_price,
            cash,
            coin_amount,
            fee
            )
        print('cash', cash)
        print('coin_amount', coin_amount)

        if position == 'buy':
            coin_amount = cash/(current_price)*(1-fee)
            cash = 0
            reference_price=current_price
            bot_price=reference_price*(1-pct_gap)
            top_price=reference_price*(1+2*fee)

            buy_points['index'].append(date)
            buy_points['data'].append(current_price)        

        elif position == 'sell':
            print('OLA')
            cash = coin_amount*current_price*(1-fee)
            coin_amount = 0
            reference_price=current_price
            bot_price=reference_price*(1-2*fee)
            top_price=reference_price*(1+pct_gap)

            sell_points['index'].append(date)
            sell_points['data'].append(current_price) 

        value = coin_amount*current_price+cash
        trading_value.append(value)


    return pd.Series(data=trading_value, index=price_series.index), pd.Series(buy_points), pd.Series(sell_points)



if __name__=='__main__':

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['BTC'].loc[datetime.datetime(2018,1,27):].resample('30T').last()

    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*100.0/price_data.iloc[0]

    strategy_result, buy, sell = adv_stop_loss_strategy(price_series=price_data)

    backtest_df['strategy'] = strategy_result

    fig, ax = plt.subplots(2,1, sharex=True)
    backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    price_data.plot(ax=ax[1])
    buy.plot(ax=ax[1], style='go')
    sell.plot(ax=ax[1], style='rx')

    plt.show()
