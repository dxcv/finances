from coinmarketcap import Market


from datetime import datetime

import coinmarketcap_history
from crypto_data import get_quandl_data
import pandas as pd

import os

convert_name_dictionary={
    'BTC': 'bitcoin',
    'DASH': 'dash',
    'XMR': 'monero',
    'BCH': 'bitcoin-cash',
    'NEO': 'neo',
    'NEM': 'nem',
    'ETH': 'ethereum',
    'XRP': 'ripple',
    'LTC': 'litecoin',
    'ADA': 'cardano',
    'UBQ': 'ubiq',
    'BIS': 'bismuth',
    'IOTA': 'iota',
    'EMC2': 'einsteinium',
    'TRX': 'tron',
    'FUN': 'funfair',
    'XLM': 'stellar',
    'ADST': 'adshares'
}

coinmarketcap = Market()

def get_coin_current_value(crypto_code, currency='eur'):
    crypto_name = convert_name_dictionary[crypto_code]
    coin = coinmarketcap.ticker(crypto_name, convert='EUR')
    value = coin[0]['price_{}'.format(currency)]
    return float(value)


def get_coin_historical_data(
    crypto_code,
    start_date='2013-01-11',
    end_date=datetime.now(),
    currency='eur'
    ):
    """
    start_date : date in YYYY-mm-dd format
    """

    if isinstance(end_date, datetime):
        end_date = end_date.strftime('%Y-%m-%d')

    crypto_name = convert_name_dictionary[crypto_code]
    df_history_usd = coinmarketcap_history.main([crypto_name, start_date, end_date, '--dataframe'])

    if currency == 'usd':
        return df_history_usd

    else:
        eur_df = get_quandl_data('ECB/EURUSD')
        df_history_eur = pd.concat([eur_df, df_history_usd], axis=1).fillna(method='ffill').dropna()
        for column in ['Open', 'High', 'Low', 'Close']:
            df_history_eur[column] = df_history_eur[column]/df_history_eur['Value']
        df_history_eur=df_history_eur.drop('Value', axis=1)
        return df_history_eur

def get_single_coin_historical_value(
    crypto_code,
    start_date='2013-01-11',
    end_date=datetime.now(),
    currency='eur'
    ):
    price_df = get_coin_historical_data(
        crypto_code=crypto_code,
        start_date='2013-01-11',
        end_date=datetime.now(),
        currency=currency
        )
    price_df = price_df.rename(columns={'Close': crypto_code})

    return price_df[crypto_code]

def get_coin_historical_value(
    crypto_code_list,
    start_date='2013-01-11',
    end_date=datetime.now(),
    currency='eur'
    ):
    total_df = pd.DataFrame()
    for coin in crypto_code_list:
        coin_df = get_single_coin_historical_value(
            crypto_code=coin,
            start_date='2013-01-11',
            end_date=datetime.now(),
            currency='eur'
            )

        total_df=pd.concat([total_df, coin_df], axis=1).fillna(method='ffill').dropna(how='all')

    return total_df


if __name__=='__main__':
    import pylab as plt

    df_eur = get_coin_historical_value(convert_name_dictionary.keys(), currency='eur')
    print(df_eur)

    df_eur.plot()
    plt.show()


    # path = 'C:\\Users\\Pedro\\Dropbox\\repository\\projects\\finances.git\\finances\\market\\data_base'
    # df_eur.to_csv(os.path.join(path, 'crypto_currencies', 'main_crypto_eur_database.csv'))
    # plt.show()