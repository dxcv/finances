import pandas as pd
import datetime
import pickle
import os
import numpy as np
import random
from finances.market import market_data as mkt_data
from finances.trading.strategies.dynamic_stoploss_strategy import dynamic_stoploss_strategy

cfd, cfn = os.path.split(os.path.abspath(__file__))


def run_strategy(
    price_series,
    pct_gap,
    minimum_gain,
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

    # sell_points = {'index':[], 'data':[]}
    # buy_points = {'index':[], 'data':[]}

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
            reinvest_gap=0.35
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
            coin_amount = current_cash/(current_price)*(1-fee)
            current_cash = 0
            # buy_points['index'].append(date)
            # buy_points['data'].append(current_price)

        elif position == 'sell':
            current_cash = coin_amount*current_price*(1-fee)
            coin_amount = 0
            # sell_points['index'].append(date)
            # sell_points['data'].append(current_price)


        value = coin_amount*current_price+current_cash
        trading_value.append(value)


    # buy_data = pd.Series(index=buy_points['index'], data=buy_points['data'])
    # sell_data = pd.Series(index=sell_points['index'], data=sell_points['data'])
    return pd.Series(data=trading_value, index=price_series.index)#, buy_data, sell_data



if __name__=='__main__':
    import pylab as plt

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['ETH'].loc[datetime.datetime(2018,1,26):].resample('4H').last()

    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*100.0/price_data.iloc[0]

    strategy_result=run_strategy(
        price_data,
        pct_gap=0.035,
        minimum_gain=0.0175,
        fee=0.0025,
        invested_value=100)

    backtest_df['strategy'] = strategy_result

    fig, ax = plt.subplots(2,1, sharex=True)
    backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    price_data.plot(ax=ax[1])
    # buy.plot(ax=ax[1], style='go')
    # sell.plot(ax=ax[1], style='rx')

    plt.show()
