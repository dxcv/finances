import pandas as pd
import datetime
import pickle
import os

from finances.market.market_data import MarketData
from finances.portfolio.portfolio import PortFolio


if __name__=='__main__':

    new_portfolio_assets = {
        'BTC': 0.11307681,
        'ETH': 1.23513731,
        'LTC': 3.37977291,
        'XRP': 757.544071,
        'DASH': 0.146593,
        'XMR': 0.59067,
        'IOTA': 47.553,
        'ADA': 217.639,
        'XLM': 140.07,
        'TRX': 0.237,
        'BCH': 0.305129,
        'FUN': 0.447,
        'EMC2': 45,
        'UBQ': 18.22222222,
        'BIS': 36.59233533,
        'ADST': 136.71,
        'NEO': 1.297627,
    }

    import pylab as plt
    import seaborn as sns
    from pprint import pprint

    sns.set()
    
    myportfolio = PortFolio(
        name= 'PedroPortfolio',
        # assets_prices = assets_effective_price
        )

    myportfolio.insert_assets_at_date(assets=new_portfolio_assets, date=datetime.datetime(2018,4,3))
    myportfolio.update_data()
    myportfolio.save_data()
    
    myportfolio.values_data.plot(style={'TOTAL':'--k'})
    plt.show()
