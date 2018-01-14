import pandas as pd
from datetime import datetime
import pickle
import os

import crypto_currencies.coin_marketcap as market

cfd, cfn = os.path.split(os.path.abspath(__file__))

class PortFolio():
	name = 'MyPortfolio'
	assets = {}
	value = 0
	invest = 0
	prices_history = pd.DataFrame()
	assets_history = pd.DataFrame()
	value_history = pd.DataFrame()

	def __init__(self, name, assets, invested):
		self.assets = assets
		self.invested = invested
		self.name = name


	def set_data_from_path(self, path=os.path.join(cfd)):
		f = open(os.path.join(path, self.name, 'prices_history.pk'), 'rb')
		self.prices_history = pickle.load(f)

		f = open(os.path.join(path, self.name, 'assets_history.pk'), 'rb')
		self.assets_history = pickle.load(f)

		self.portfolio_path = os.path.join(path, self.name)


	def update_value(self):
		value = 0
		for asset in self.assets:
			asset_value= market.get_coin_value(asset)
			value += self.assets[asset]*asset_value
			print(asset, asset_value, self.assets[asset]*asset_value)
		self.value = value

	def update_prices_history(self, name='prices_history'):
		temp_df = pd.DataFrame(index=[datetime.now().replace(second=0, microsecond=0)])

		for asset in self.assets:
			temp_df[asset] = market.get_coin_value(asset)

		self.prices_history = self.prices_history.append(temp_df)
		self.prices_history.to_pickle(os.path.join(self.portfolio_path, name+'.pk'))
		self.prices_history.to_csv(os.path.join(self.portfolio_path, name+'.csv'))

	def update_assets_history(self, name='assets_history'):
		temp_df = pd.DataFrame(self.assets, index=[datetime.now().replace(second=0, microsecond=0)])
		self.assets_history = self.assets_history.append(temp_df)

		self.assets_history.to_pickle(os.path.join(self.portfolio_path, name+'.pk'))
		self.assets_history.to_csv(os.path.join(self.portfolio_path, name+'.csv'))

	def update_portfolio_history(self, assets_name, prices_name):
		self.update_prices_history(name=prices_name)
		self.update_assets_history(name=assets_name)

	def  create_value_dataframe(self):
		for asset in self.assets_history.columns:
			self.value_history[asset] = self.prices_history[asset]*self.assets_history[asset]
		return self.value_history






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

	import pylab as plt
	from pprint import pprint
	
	myportfolio = PortFolio(name= 'MyPortfolio', assets = portfolio_assets, invested = 2270.0)
	myportfolio.set_data_from_path(path=os.path.join(cfd))

	# myportfolio.update_portfolio_history(assets_name='assets_history', prices_name='prices_history')
	print(myportfolio.assets_history)
	print(myportfolio.prices_history)

	print('#################################################################')
	values_df = myportfolio.create_value_dataframe()
	values_df.plot()
	plt.show()


