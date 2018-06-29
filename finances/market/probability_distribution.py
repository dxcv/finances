import pandas as pd
import datetime
import pickle
import os
import portfolioopt as pfopt
import numpy as np
import pylab as plt

from scipy.stats import norm
from finances.market import market_data as mkt_data
import statsmodels.api as sm

cfd, cfn = os.path.split(os.path.abspath(__file__))

mkt=mkt_data.MarketData()

hourly_returns = mkt.crypto_returns_data(
    symbols=['ADA', 'XMR', 'BTC', 'NEO', 'EMC2', 'ETH', 'FUN', 'IOTA', 'LTC', 'TRX', 'UBQ', 'XLM', 'XRP'],
    time_step='H',
    start_date = datetime.datetime(2018,1,26)
    ).dropna()

daily_returns = mkt.crypto_returns_data(
    symbols=['ADA', 'XMR', 'BTC', 'NEO', 'EMC2', 'ETH', 'FUN', 'IOTA', 'LTC', 'TRX', 'UBQ', 'XLM', 'XRP'],
    time_step='D',
    start_date = datetime.datetime(2018,1,26)
    ).dropna()

print(hourly_returns)

month_returns = pd.DataFrame()


n_days = 24
x = np.linspace(-0.5,0.5,1000)

# plot density of returns

fig = plt.figure(figsize=(10,10))
f = 1
for r in hourly_returns.columns:
    # calculate the distributions
    rets = hourly_returns[r].dropna()
    daily_mu, daily_std = norm.fit(rets)
    monthly_mu, monthly_std = n_days*daily_mu, daily_std*np.sqrt(n_days)
    monthly_data = norm.rvs(monthly_mu, monthly_std, size=1000)
    month_returns[r] = monthly_data

    # get the pdf of the variables
    p_daily = norm.pdf(x, daily_mu, daily_std)
    p_monthly = norm.pdf(x, monthly_mu, monthly_std)

    # create the figures
    fig.add_subplot(4,4,f)
    ax = plt.gca()
    plt.plot(x, p_daily, label='Daily')
    plt.plot(x, p_monthly, label='Monthly')
    plt.hist(hourly_returns[r].dropna(), bins=25, normed=True)
    plt.hist(daily_returns[r].dropna(), bins=25, normed=True, alpha=0.5)

    f+=1
    ax.set_title('{}, {} values'.format(r, len(rets)))
    # ax.set_ylim(0,12)
    ax.set_xlim(-0.2,0.2)
plt.legend()
plt.show()


