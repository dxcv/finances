
import pandas as pd
import datetime
import os
import numpy as np
import pylab as plt
import random
from finances.market import market_data as mkt_data
import statsmodels.api as sm

from finances.trading.strategies.stoploss import adv_stop_loss_strategy
from finances.trading.strategies.variable_stoploss import dynamic_stoploss_strategy
from finances.trading.backtest import back_test_all

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()

results_df = pd.DataFrame()

pct_gap_range = np.arange(0.01,0.05,0.005)
times = ['H', '2H', '4H', '6H', '8H']
min_gain_range = np.arange(0.0025, 0.05, 0.0025)


results_df_list=[]

for period in times:
    for pct_gap in pct_gap_range:
        for min_gain in min_gain_range:
            price_data = mkt.crypto_data['BTC'].loc[datetime.datetime(2018,1,26):].resample(period).last()
            print(period, pct_gap, min_gain)

            def strategy_to_sweep(price_series):
                return dynamic_stoploss_strategy(
                    price_series,
                    pct_gap=pct_gap,
                    minimum_gain=min_gain,
                    fee=0.0025,
                    invested_value=100)

            df = back_test_all(
                price_data,
                time_delta_stress_test=datetime.timedelta(days=40),
                strategy=strategy_to_sweep,
                view_result=False)

            df['pct_gap'] = pct_gap
            df['min_gain'] = min_gain
            df['period'] = period
            results_df_list.append(df[['strategy', 'min_gain', 'pct_gap', 'period']])
            results_df = pd.concat(results_df_list)
            results_df.to_csv(os.path.join(cfd, 'dynamic_stoploss_strategy.csv'))
