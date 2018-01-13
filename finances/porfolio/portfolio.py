import pandas as pd

import crypto_currencies.coin_marketcap as market


class PortFolio():
	assets = {}
	historical_value = pd.DataFrame()
	transactions = pd.DataFrame()
	value = 0
	invested = 0

	def __init__(self, assets, invested):
		self.assets = assets
		self.invested = invested

	def update_value(self):
		value = 0
		for asset in self.assets:
			asset_value= market.get_coin_value(asset)
			value += self.assets[asset]*asset_value
		self.value = value





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
