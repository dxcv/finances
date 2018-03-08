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

def strategy_decision(
    current_price,
    decision_price,
    stoploss_value,
    cash,
    coin_amount,
    state,
    reinvest_gap=0.3,
    pct_gap=0.025,
    fee=0.0025):

    if cash==0 and coin_amount>0:
        if decision_price < stoploss_value*(1-pct_gap) and state == 0:
            cash = coin_amount*current_price*(1-fee)
            coin_amount = 0
            stoploss_value=current_price

        elif decision < stoploss_value*(1+pct_gap) and state == 1:
            cash = coin_amount*current_price*(1-fee)
            coin_amount = 0
            # stoploss_value=current_price


        elif decision_price>stoploss_value*(1+reinvest_gap) and state==1:
            stoploss_value=stoploss_value*(1+reinvest_gap)

    elif coin_amount==0 and cash>0:
        if decision_price > stoploss_value*(1+pct_gap) and state==0:
            coin_amount = cash/(current_price)*(1-fee)
            cash = 0
            stoploss_value=current_price

        elif decision_price > stoploss_value*(1-pct_gap) and state == -1:
            coin_amount = cash/(current_price)*(1-fee)
            cash = 0
            stoploss_value=current_price

        elif decision_price<stoploss_value*(1-reinvest_gap) and state==-1:
            coin_amount = cash/(stoploss_value*(1-reinvest_gap))*(1-fee)
            cash = 0
            stoploss_value=stoploss_value*(1-reinvest_gap)
    
    return cash, coin_amount, stoploss_value



def stop_loss_strategy(price_series, pct_gap=pct_gap, fee=0.0025, invested_value=100):
    stoploss_value = price_series.iloc[0]

    coin_amount = invested_value/price_series.iloc[0]
    cash = 0

    trade_value = [invested_value]
    stoploss=[stoploss_value]
    state = 0
    for k in range(1,len(price_series)):
        current_price = price_series.iloc[k]

        cash, coin_amount, stoploss_value = strategy_decision(
            current_price=current_price,
            cash=cash,
            stoploss_value=stoploss_value,
            coin_amount=coin_amount,
            state=state,
            reinvest_gap=reinvest_gap,
            pct_gap=pct_gap,
            fee=fee)

        if current_price >= stoploss_value*(1+pct_gap):
            state=1

        elif current_price <= stoploss_value*(1-pct_gap):
            state=-1

        else:
            state=0

        value = coin_amount*current_price+cash
        trade_value.append(value)
        stoploss.append(stoploss_value)

    return pd.Series(data=trade_value, index=price_series.index), pd.Series(data=stoploss, index=price_series.index)


def adv_stop_loss_strategy(price_series, reinvest_gap=0.2, pct_gap=pct_gap, fee=0.0025, invested_value=100):
    stoploss_value = price_series.iloc[0]

    coin_amount = invested_value/price_series.iloc[0]
    cash = 0

    trade_value = [invested_value]
    stoploss=[stoploss_value]
    state = 0
    for k in range(1,len(price_series)):
        current_price = price_series.iloc[k]

        cash, coin_amount, stoploss_value = strategy_decision(
            current_price=current_price,
            decision_price=current_price,
            cash=cash,
            stoploss_value=stoploss_value,
            coin_amount=coin_amount,
            state=state,
            reinvest_gap=reinvest_gap,
            pct_gap=pct_gap,
            fee=fee)

        # check state

        if decision_price >= stoploss_value*(1+pct_gap):
            state=1

        elif decision_price <= stoploss_value*(1-pct_gap):
            state=-1

        else:
            state=0

        value = coin_amount*current_price+cash
        trade_value.append(value)
        stoploss.append(stoploss_value)

    return pd.Series(data=trade_value, index=price_series.index), pd.Series(data=stoploss, index=price_series.index)



if __name__=='__main__':

    mkt=mkt_data.MarketData()

    price_data = mkt.crypto_data['BTC'].loc[datetime.datetime(2017,11,1):].dropna()

    backtest_df = pd.DataFrame()
    backtest_df['price'] = price_data
    backtest_df['hold'] = price_data*100.0/price_data.iloc[0]

    strategy_result, stop=adv_stop_loss_strategy(price_series=price_data)

    backtest_df['strategy'] = strategy_result


    backtest_df['strategy'] = strategy_result

    #
    backtest_df['stop'] = stop
    backtest_df['stop_+'] = stop*(1+pct_gap)
    backtest_df['stop_-'] = stop*(1-pct_gap)

    fig, ax = plt.subplots(2,1, sharex=True)
    backtest_df[['strategy', 'hold']].plot(ax=ax[0])
    price_data.plot(ax=ax[1])
    backtest_df['stop'].plot(ax=ax[1], style='k')
    backtest_df['stop_+'].plot(ax=ax[1], style='g')
    backtest_df['stop_-'].plot(ax=ax[1], style='r')

    plt.show()
