from coinmarketcap import Market

convert_name_dictionary={
    'BTC': 'bitcoin',
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

def get_coin_value(crypto_code, currency='eur'):
    crypto_name = convert_name_dictionary[crypto_code]
    coin = coinmarketcap.ticker(crypto_name, convert='EUR')
    value = coin[0]['price_{}'.format(currency)]
    return float(value)


if __name__=='__main__':
    for coin_code in convert_name_dictionary:
        print(get_coin_value(coin_code))