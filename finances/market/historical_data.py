import coinmarketcap_history

df = coinmarketcap_history.main(['adshares','2015-01-01','2018-01-16','--dataframe'])

print(df)

import pylab as plt
df.plot()
plt.show()