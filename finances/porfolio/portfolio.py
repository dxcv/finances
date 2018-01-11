import pandas as pd

from crypto_currencies import crypto_data


class PortFolio():

	allocation = {}
	historical_value = pd.DataFrame()
	transactions = pd.DataFrame()
	value = 0

	def __init__(self, allocation):
		self.allocation = allocation

	def update_value(self):
		value = 0
		for asset in self.allocation:
			asset_value = crypto_data.get_btc_price('Close')[-1]
			value += self.allocation[asset]*asset_value
		self.value = value





if __name__=='__main__':
	a = PortFolio({'BTC':0.5, 'ETH':0.5})
	a.update_value()
	print(a.value)