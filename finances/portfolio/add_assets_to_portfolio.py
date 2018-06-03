import pandas as pd
import datetime
import pickle
import os

from finances.market.market_data import MarketData
from finances.portfolio.portfolio import PortFolio


if __name__=='__main__':

    new_portfolio_assets = {
        'BTC': 0.08060001625,
        'ETH': 1.07980135,
        'LTC': 3.03879891,
        'XRP': 627.1118061,
        'DASH': 0.167572,
        'XMR': 0.722538,
        'IOTA': 136.464,
        'ADA': 552.304,
        'XLM': 467.742,
        'TRX': 1405.83,
        'BCH': 0.303937,
        'FUN': 0.447,
        'EMC2': 45,
        'UBQ': 18.22222222,
        'BIS': 36.59233533,
        'ADST': 136.71,
        'NEO': 1.577347,
        'EOS': 7.992,
        'ONT': 7.4076627,
    }

    import pylab as plt
    import seaborn as sns
    from pprint import pprint

    sns.set()
    
    myportfolio = PortFolio(
        name= 'PedroPortfolio',
        # assets_prices = assets_effective_price
        )

    myportfolio.insert_assets_at_date(assets=new_portfolio_assets, date=datetime.datetime(2018,6,3))
    myportfolio.update_data()
    myportfolio.save_data()
    
    myportfolio.values_data.plot(style={'TOTAL':'--k'})
    plt.show()
