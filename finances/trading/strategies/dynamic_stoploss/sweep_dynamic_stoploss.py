import pandas as pd
import datetime
import os
import numpy as np
import sys
import random

cfd, cfn = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(cfd, '..', '..', '..'))

from finances.market import market_data as mkt_data
from finances.trading.strategies.dynamic_stoploss.dynamic_stoploss_strategy import run_dynamic_stoploss_strategy
from finances.trading.strategies.backtest_strategy import backtest_dates_set
from pprint import pprint

mkt=mkt_data.MarketData()

results_df = pd.DataFrame()

pct_gap_range = np.arange(0.01,0.11,0.01)
times = ['4H', '6H', '8H', '12H', '24H']
min_gain_range = np.arange(0.01,0.11,0.01)

results_df_list=[]

for coin in ['BTC', 'ETH', 'LTC', 'XRP', 'BCH', 'XLM', 'ADA', 'TRX', 'NEO', 'IOTA']:
    for period in times:

        backtest_period=datetime.timedelta(days=30)
        n_dates = 100

        start = datetime.datetime(2018,1,26)

        # select the dates to run the analysis into
        price_data = mkt.crypto_data[coin].loc[start:].resample(period).last()
        start_dates = price_data.loc[:price_data.index[-1]-backtest_period].index
        random.seed(1234)
        selected_start_dates = random.sample(list(start_dates),n_dates)
        pprint(sorted(selected_start_dates))

        for pct_gap in pct_gap_range:
            for min_gain in min_gain_range:
                print(coin, period, pct_gap, min_gain)

                def strategy_to_sweep(price_series, invested_value=100):
                    return run_dynamic_stoploss_strategy(
                        price_series,
                        pct_gap=pct_gap,
                        minimum_gain=min_gain,
                        fee=0.0025,
                        invested_value=invested_value)

                df = backtest_dates_set(
                    price_data,
                    strategy_run=strategy_to_sweep,
                    start_dates_set=selected_start_dates,
                    time_delta_stress_test=backtest_period,
                    view_result=False)

                df['pct_gap'] = pct_gap
                df['min_gain'] = min_gain
                df['period'] = period
                results_df_list.append(df[['strategy', 'min_gain', 'pct_gap', 'period']])
                results_df = pd.concat(results_df_list)
                results_df.to_csv(os.path.join(cfd, 'dynamic_stoploss_strategy_{}_Maio.csv'.format(coin)))

        # add hold strategy
        df['pct_gap'] = 0
        df['min_gain'] = 0
        df['period'] = period
        df['strategy'] = df['hold']
        results_df_list.append(df[['strategy', 'min_gain', 'pct_gap', 'period']])
        results_df = pd.concat(results_df_list)

        # save the file
        results_df.to_csv(os.path.join(cfd, 'dynamic_stoploss_strategy_{}_Maio.csv'.format(coin)))
