import pandas as pd
from datetime import datetime
import pickle
import os

import crypto_currencies.coin_marketcap as market

cfd, cfn = os.path.split(os.path.abspath(__file__))

class PortFolio():
	assets = {}
	historical_value = pd.DataFrame()
	transactions = pd.DataFrame()
	value = 0
	invested = 0
	portfolio_location = os.path.join(cfd, 'my_portfolio.pk')

	def __init__(self, assets, invested):
		self.assets = assets
		self.invested = invested
		f = open(self.portfolio_location, 'rb')
		self.historical_value = pickle.load(f)

	def update_value(self):
		value = 0
		for asset in self.assets:
			asset_value= market.get_coin_value(asset)
			value += self.assets[asset]*asset_value
			print(asset, asset_value, self.assets[asset]*asset_value)
		self.value = value

	def save_portfolio_prices(self):
		pd.DataFrame(index=[datetime.now()])
		temp_df = pd.DataFrame(index=[datetime.now()])

		for asset in self.assets:
			temp_df[asset] = market.get_coin_value(asset)

		self.historical_value = self.historical_value.append(temp_df)
		print(self.historical_value)
		self.historical_value.to_pickle(self.portfolio_location)
		self.historical_value.to_csv(os.path.join(cfd, 'my_portfolio.csv'))








if __name__=='__main__':
	portfolio_assets = {
		'BTC': 0.007,
		'ETH': 2.14081,
		'XRP': 922.5,
		'ADA': 926,
		'XLM': 929.07,
		'LTC': 1.0,
		'TRX': 2760,
		'UBQ': 18.222,
		'BIS': 36.6,
		'IOTA': 47.553,
		'EMC2': 45,
		'FUN': 633.366,
		'ADST': 136.71
	}

	myportfolio = PortFolio(assets = portfolio_assets, invested = 2270.0)
	myportfolio.update_value()
	print(myportfolio.value)

	myportfolio.save_portfolio_prices()

	from pprint import pprint
	pprint(myportfolio)