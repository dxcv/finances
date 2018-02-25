import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt
from market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))


def stop_loss_strategy(price_series, pct_gap=0.01, fee=0.0025, invested_value=100):
    stoploss_value = price_series.iloc[0]

    coin_amount = invested_value/price_series.iloc[0]
    cash = 0

    trade_value = [invested_value]
    state = 0
    for k in range(1,len(price_series)):
        current_price = price_series.iloc[k]

        if current_price < stoploss_value*(1+pct_gap) and state>0 and cash==0:
            cash = coin_amount*stoploss_value*(1+pct_gap)*(1-fee)
            coin_amount = 0

        elif current_price > stoploss_value*(1-pct_gap) and state<0 and coin_amount==0:
            coin_amount = cash/(stoploss_value*(1-pct_gap))*(1-fee)
            cash = 0
            stoploss_value = stoploss_value*(1-pct_gap)

        if current_price >= stoploss_value*(1+pct_gap):
            state=1

        elif current_price <= stoploss_value*(1-pct_gap):
            state=-1

        else:
            state=0

        value = coin_amount*current_price+cash
        trade_value.append(value)

    return pd.Series(data=trade_value, index=price_series.index)



mkt=mkt_data.MarketData()

price_data = mkt.crypto_data['BTC'].dropna().loc[datetime.datetime(2018,1,27):]

df = pd.DataFrame()
df['price'] = price_data
df['hold'] = price_data*100.0/price_data.iloc[0]

strategy=stop_loss_strategy(price_series=price_data)

df['strategy'] = strategy

stoploss_value = price_data.iloc[0]
print(df.index[0])

fig, ax = plt.subplots(2,1, sharex=True)
df[['strategy', 'hold']].plot(ax=ax[0])
df[['price']].plot(ax=ax[1])
ax[1].plot([df.index[0],df.index[-1]],[stoploss_value,stoploss_value], 'k--')
ax[1].plot([price_data.index[0],price_data.index[-1]],[stoploss_value*(1+0.01),stoploss_value*(1+0.01)], 'g--')
ax[1].plot([price_data.index[0],price_data.index[-1]],[stoploss_value*(1-0.01),stoploss_value*(1-0.01)], 'r--')

# print(df)
plt.show()
