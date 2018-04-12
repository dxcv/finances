import pandas as pd
import datetime
import pickle
import os
import numpy as np
import random
from finances.market import market_data as mkt_data
from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import run_dynamic_stoploss_strategy

cfd, cfn = os.path.split(os.path.abspath(__file__))


def backtest_strategy(price_data, strategy_run, initial_investment=100):
    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*initial_investment/price_data.iloc[0]

    strategy_result=strategy_run(price_series=price_data, invested_value=initial_investment)
    backtest_df['strategy'] = strategy_result

    return backtest_df

def back_test_random(
    price_data,
    strategy_run,
    n=200,
    time_delta_stress_test=datetime.timedelta(days=30),
    view_result=False
    ):

    np.random.seed(seed=1234)
    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}
    date_list=[]
    for k in [np.random.randint(len(price_data.index)) for i in range(n)]:
        start_test = price_data.index[k]
        end_test=start_test+time_delta_stress_test

        prices_test_data = price_data.loc[start_test:end_test]
        if prices_test_data.index[-1]-prices_test_data.index[0]<time_delta_stress_test:
            continue

        date_list.append(start_test)

        backtest_df = backtest_strategy(
            price_data=prices_test_data,
            strategy_run=strategy_run,
            initial_investment=100)

        if view_result:
            if n>25:
                raise('Sample too big. Reduce number of tests')
            fig, ax = plt.subplots(2,1, sharex=True)
            backtest_df[['strategy', 'hold']].plot(ax=ax[0])
            prices_test_data.plot(ax=ax[1])

        for t in ['hold', 'strategy']:
            compare_dic[t].append(backtest_df[t].iloc[-1]-100.0)

        compare_dic['diff'].append(backtest_df['strategy'].iloc[-1]-backtest_df['hold'].iloc[-1])

    return pd.DataFrame(data=compare_dic, index=date_list)


def back_test_all(
    price_data,
    strategy,
    time_delta_stress_test=datetime.timedelta(days=30),
    view_result=False
    ):

    np.random.seed(seed=1234)
    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}
    date_list=[]
    n_dates = len(price_data.loc[:(price_data.index[-1]-time_delta_stress_test)])

    for k in range(n_dates):
        start_test = price_data.index[k]
        end_test=start_test+time_delta_stress_test

        prices_test_data = price_data.loc[start_test:end_test]
        if prices_test_data.index[-1]-prices_test_data.index[0]<time_delta_stress_test:
            continue

        date_list.append(start_test)

        backtest_df = pd.DataFrame()

        backtest_df['hold'] = prices_test_data*100.0/prices_test_data.iloc[0]

        strategy_result=strategy(price_series=prices_test_data)

        backtest_df['strategy'] = strategy_result


        if view_result:
            fig, ax = plt.subplots(2,1, sharex=True)
            backtest_df[['strategy', 'hold']].plot(ax=ax[0])
            prices_test_data.plot(ax=ax[1])
            plt.show()

        for t in ['hold', 'strategy']:
            compare_dic[t].append(backtest_df[t].iloc[-1]-100.0)

        compare_dic['diff'].append(backtest_df['strategy'].iloc[-1]-backtest_df['hold'].iloc[-1])

    return pd.DataFrame(data=compare_dic, index=date_list)



if __name__=='__main__':
    import pylab as plt

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['ETH'].loc[datetime.datetime(2018,1,26):].resample('4H').last()

    # backtest_df=backtest_strategy(price_data)

    # fig, ax = plt.subplots(2,1, sharex=True)
    # backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    # price_data.plot(ax=ax[1])
    # # buy.plot(ax=ax[1], style='go')
    # # sell.plot(ax=ax[1], style='rx')

    # plt.show()


    df = back_test_random(
        price_data=price_data,
        strategy_run=run_dynamic_stoploss_strategy,
        n=20,
        time_delta_stress_test=datetime.timedelta(days=30),
        view_result=False
        )

    df.boxplot()
    plt.show()