import pandas as pd
import datetime
import pickle
import os
import numpy as np
import random
from finances.market import market_data as mkt_data
from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import run_dynamic_stoploss_strategy

cfd, cfn = os.path.split(os.path.abspath(__file__))


def backtest_strategy(price_data, strategy_run, initial_investment=100, debug=False):
    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*initial_investment/price_data.iloc[0]

    strategy_result=strategy_run(price_series=price_data, invested_value=initial_investment, debug=debug)
    backtest_df['strategy'] = strategy_result

    return backtest_df


def backtest_dates_set(
    price_data,
    strategy_run,
    start_dates_set,
    time_delta_stress_test=datetime.timedelta(days=30),
    view_result=False
    ):

    initial_investment=100
    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}

    for start_test in start_dates_set:
        end_test=start_test+time_delta_stress_test

        prices_data_test = price_data.loc[start_test:end_test]

        backtest_df = backtest_strategy(
            price_data=prices_data_test,
            strategy_run=strategy_run,
            initial_investment=initial_investment)

        if view_result:
            if n>25:
                raise('Sample too big. Reduce number of tests')
            fig, ax = plt.subplots(2,1, sharex=True)
            backtest_df[['strategy', 'hold']].plot(ax=ax[0])
            prices_data_test.plot(ax=ax[1])

        for t in ['hold', 'strategy']:
            compare_dic[t].append(backtest_df[t].iloc[-1]-initial_investment)

        compare_dic['diff'].append(backtest_df['strategy'].iloc[-1]-backtest_df['hold'].iloc[-1])

    return pd.DataFrame(data=compare_dic, index=start_dates_set)


def backtest_random(
    price_data,
    strategy_run,
    n=200,
    time_delta_stress_test=datetime.timedelta(days=10),
    view_result=False
    ):

    initial_investment=100

    np.random.seed(seed=1234)
    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}

    start_dates = price_data.loc[:price_data.index[-1]-time_delta_stress_test].index
    random_dates_index = [np.random.randint(len(start_dates)) for i in range(n)]
    selected_start_dates = [start_dates[i] for i in random_dates_index]

    return backtest_dates_set(
        price_data,
        strategy_run,
        start_dates_set=selected_start_dates,
        time_delta_stress_test=time_delta_stress_test,
        view_result=view_result
        )

def backtest_all(
    price_data,
    strategy_run,
    time_delta_stress_test=datetime.timedelta(days=10),
    view_result=False
    ):

    initial_investment=100

    np.random.seed(seed=1234)
    compare_dic = {'hold':[], 'strategy':[], 'diff':[]}

    start_dates = price_data.loc[:price_data.index[-1]-time_delta_stress_test].index
    selected_start_dates=start_dates

    return backtest_dates_set(
        price_data,
        strategy_run,
        start_dates_set=selected_start_dates,
        time_delta_stress_test=time_delta_stress_test,
        view_result=view_result
        )



if __name__=='__main__':
    import pylab as plt

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['TRX'].loc[datetime.datetime(2018,2,10):].resample('8H').last()

    backtest_df=backtest_strategy(price_data,strategy_run=run_dynamic_stoploss_strategy)

    fig, ax = plt.subplots(2,1, sharex=True)
    backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    price_data.plot(ax=ax[1])
    # buy.plot(ax=ax[1], style='go')
    # sell.plot(ax=ax[1], style='rx')

    plt.show()


    # df = backtest_random(
    #     price_data=price_data,
    #     strategy_run=run_dynamic_stoploss_strategy,
    #     n=100,
    #     time_delta_stress_test=datetime.timedelta(days=10),
    #     view_result=False
    #     )

    # df.boxplot()
    # plt.show()