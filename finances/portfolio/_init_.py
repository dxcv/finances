import pandas as pd


class PortFolio():

	allocation = {}
	value = 0

	def __init__(self, allocation):
		self.allocation = allocation

	def get_value(self):
		for asset in self.allocation:
			asset_value = 



if __name__=='__main__':
	a = PortFolio({'BTC':0.5, 'ETH':0.5})
	print(a.allocation)