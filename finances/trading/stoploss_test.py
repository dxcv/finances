import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt
import random
from market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))


def stop_loss_strategy(price_series, pct_gap=0.0, fee=0.0025, invested_value=100):
    stoploss_value = price_series.iloc[0]

    coin_amount = invested_value/price_series.iloc[0]
    cash = 0

    trade_value = [invested_value]
    state = 0
    for k in range(1,len(price_series)):
        current_price = price_series.iloc[k]

        if cash==0 and coin_amount>0:
            if current_price < stoploss_value*(1-pct_gap) and state == 0:
                cash = coin_amount*stoploss_value*(1-pct_gap)*(1-fee)
                coin_amount = 0
                # stoploss_value=stoploss_value*(1-pct_gap)

            elif current_price < stoploss_value*(1+pct_gap) and state == 1:
                cash = coin_amount*stoploss_value*(1+pct_gap)*(1-fee)
                coin_amount = 0

        elif coin_amount==0 and cash>0:
            if current_price > stoploss_value*(1+pct_gap) and state==0:
                coin_amount = cash/stoploss_value*(1+pct_gap)*(1-fee)
                cash = 0
                # stoploss_value=stoploss_value*(1+pct_gap)

            elif current_price > stoploss_value*(1-pct_gap) and state == -1:
                coin_amount = cash/stoploss_value*(1-pct_gap)*(1-fee)
                cash = 0

        # check state

        if current_price >= stoploss_value*(1+pct_gap):
            state=1

        elif current_price <= stoploss_value*(1-pct_gap):
            state=-1

        else:
            state=0

        value = coin_amount*current_price+cash
        trade_value.append(value)

    return pd.Series(data=trade_value, index=price_series.index)


def back_test_random(price_data, n=350, time_delta_stress_test=datetime.timedelta(days=30)):

    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}
    date_list=[]
    for k in range(n):
        start_test = random.choice(price_data.index)
        end_test=start_test+time_delta_stress_test
        date_list.append(start_test)
        
        prices_test_data = price_data.loc[start_test:end_test]
        backtest_df = pd.DataFrame()

        backtest_df['hold'] = prices_test_data*100.0/prices_test_data.iloc[0]

        strategy=stop_loss_strategy(price_series=prices_test_data)

        backtest_df['strategy'] = strategy

        # fig, ax = plt.subplots(2,1, sharex=True)
        # backtest_df[['strategy', 'hold']].plot(ax=ax[0])
        # prices_test_data.plot(ax=ax[1])

        for t in ['hold', 'strategy']:
            compare_dic[t].append(backtest_df[t].iloc[-1])

        compare_dic['diff'].append(backtest_df['strategy'].iloc[-1]-backtest_df['hold'].iloc[-1])

    return pd.DataFrame(data=compare_dic, index=date_list)


if __name__=='__main__':

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['BTC'].dropna().loc[datetime.datetime(2017,1,27):]
    df = back_test_random(price_data)
    df.boxplot()

    plt.show()
    # df = pd.DataFrame()
    # df['price'] = price_data
    # df['hold'] = price_data*100.0/price_data.iloc[0]

    # strategy=stop_loss_strategy(price_series=price_data)

    # df['strategy'] = strategy

    # stoploss_value = price_data.iloc[0]
    # print(df.index[0])

    # fig, ax = plt.subplots(2,1, sharex=True)
    # df[['strategy', 'hold']].plot(ax=ax[0])
    # df[['price']].plot(ax=ax[1])
    # ax[1].plot([df.index[0],df.index[-1]],[stoploss_value,stoploss_value], 'k--')
    # ax[1].plot([price_data.index[0],price_data.index[-1]],[stoploss_value*(1+0.01),stoploss_value*(1+0.01)], 'g--')
    # ax[1].plot([price_data.index[0],price_data.index[-1]],[stoploss_value*(1-0.01),stoploss_value*(1-0.01)], 'r--')

    # # print(df)
    # plt.show()
