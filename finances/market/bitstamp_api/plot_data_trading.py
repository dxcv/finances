import pandas as pd 


df = pd.read_csv(
        'C:\\Users\\Pedro\\Desktop\\bitstamp_high_frequency_data.csv',
        index_col=0,
        parse_dates=True,
        infer_datetime_format=True)

df.btc.plot(style='-o')

import pylab as plt 

plt.show()