import pandas as pd
import datetime
import pickle
import os

from finances.market.market_data import MarketData
from finances.portfolio.portfolio import PortFolio


if __name__=='__main__':

    new_portfolio_assets = {
        'BTC': 0.04777770486,
        'ETH': 2.04903994,
        'LTC': 2.79000003,
        'XRP': 245.8,
        'DASH': 0.286593,
        'XMR': 1.18067,
        'IOTA': 47.553,
        'ADA': 433.639,
        'XLM': 279.07,
        'TRX': 0.237,
        'BCH': 0.20009,
        'FUN': 0.447,
        'EMC2': 45,
        'UBQ': 18.22222222,
        'BIS': 36.59233533,
        'ADST': 136.71,
        'NEO': 2.587627
    }

    import pylab as plt
    import seaborn as sns
    from pprint import pprint

    sns.set()
    
    myportfolio = PortFolio(
        name= 'PedroPortfolio',
        # assets_prices = assets_effective_price
        )

    # myportfolio.insert_assets_at_date(assets=new_portfolio_assets, date=datetime.datetime(2018,3,9))
    myportfolio.update_data()
    myportfolio.values_data.plot(style={'TOTAL':'--k'})
    # myportfolio.save_data()
    plt.show()


    # bitstamp_assets = {'BTC': 0, 'XRP':0, 'BCH':0 , 'LTC':0, 'ETH':0,
    # 'ADA':0, 'NEO':0, 'XLM':0, 'XMR':0, 'DASH':0}
    # new_portfolio = PortFolio()
    # new_portfolio.assets = bitstamp_assets
    # start_date = datetime.datetime(2018,2,9,2)

    # p = new_portfolio.optimize_allocation(projection_steps=30, value_to_invest=2600)
    # print(p)
    # # p.plot(style={'TOTAL':'--k'})
    # plt.show()
