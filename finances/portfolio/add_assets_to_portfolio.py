import pandas as pd
import datetime
import pickle
import os

from finances.market.market_data import MarketData
from finances.portfolio.portfolio import PortFolio


if __name__=='__main__':

    new_portfolio_assets = {
        'BTC': 0.08418145625,
        'ETH': 2.22410816,
        'LTC': 4.88320891,
        'XRP': 847.103044,
        'DASH': 0.112883,
        'XMR': 0.764838,
        'IOTA': 114.082,
        'ADA': 598.147,
        'XLM': 517.757,
        'TRX': 1502.317,
        'BCH': 0.4422602,
        'FUN': 0.447,
        'EMC2': 45,
        'UBQ': 18.22222222,
        'BIS': 36.59233533,
        'ADST': 136.71,
        'NEO': 0.771997,
        'EOS': 7.992,
        'ONT': 19.442965
    }

    import pylab as plt
    import seaborn as sns
    from pprint import pprint

    sns.set()
    
    myportfolio = PortFolio(
        name= 'PedroPortfolio',
        # assets_prices = assets_effective_price
        )

    myportfolio.insert_assets_at_date(assets=new_portfolio_assets, date=datetime.datetime(2018,8,24))
    myportfolio.update_data()
    myportfolio.save_data()
    
    myportfolio.values_data.plot(style={'TOTAL':'--k'})
    plt.show()
