
import pandas as pd
import datetime
import os
import numpy as np
import pylab as plt
import random
from market import market_data as mkt_data
import statsmodels.api as sm

from trading.strategies.stoploss import adv_stop_loss_strategy

def back_test_random(price_data, n=200, time_delta_stress_test=datetime.timedelta(days=30)):

    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}
    date_list=[]
    for k in range(n):
        start_test = random.choice(price_data.index)
        end_test=start_test+time_delta_stress_test
        date_list.append(start_test)
        
        prices_test_data = price_data.loc[start_test:end_test]
        backtest_df = pd.DataFrame()

        backtest_df['hold'] = prices_test_data*100.0/prices_test_data.iloc[0]

        strategy, stop=adv_stop_loss_strategy(price_series=prices_test_data)

        backtest_df['strategy'] = strategy

        #
        backtest_df['stop'] = stop
        backtest_df['stop_+'] = stop*(1+pct_gap)
        backtest_df['stop_-'] = stop*(1-pct_gap)

        # fig, ax = plt.subplots(2,1, sharex=True)
        # backtest_df[['strategy', 'hold']].plot(ax=ax[0])
        # prices_test_data.plot(ax=ax[1])
        # backtest_df['stop'].plot(ax=ax[1], style='k')
        # backtest_df['stop_+'].plot(ax=ax[1], style='g')
        # backtest_df['stop_-'].plot(ax=ax[1], style='r')

        for t in ['hold', 'strategy']:
            compare_dic[t].append(backtest_df[t].iloc[-1]-100.0)

        compare_dic['diff'].append(backtest_df['strategy'].iloc[-1]-backtest_df['hold'].iloc[-1])

    return pd.DataFrame(data=compare_dic, index=date_list)


if __name__=='__main__':

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['XLM'].dropna()
    df = back_test_random(price_data)
    df.boxplot()

    for c in ['hold', 'strategy']:
        sharpe = df[c].mean()/df[c].std()
        print(c, sharpe)

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
