import json

def buy_all_with_btc(trading_client, coin, btc_quantity):
    price_list={}
    for pair in trading_client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])
    current_price= price_list[coin+'BTC']
    amount_to_buy = round(btc_quantity/current_price, 3)

    bought=False
    while not bought and amount_to_buy>0:
        try:
            trading_client.order_market_buy(
                symbol=coin+'BTC',
                quantity=amount_to_buy
            )
            bought=True
            print('Bought {0} {1}'.format(amount_to_buy, coin))
        except:
            amount_to_buy=round(0.9975*amount_to_buy,6)

def sell_all_for_btc(trading_client, coin):
    coin_available = float(trading_client.get_asset_balance(asset=coin)['free'])
    amount_to_sell = coin_available

    sold=False
    while not sold and amount_to_sell>0:
        try:
            trading_client.order_market_sell(
                symbol=coin+'BTC',
                quantity=amount_to_sell
            )
            sold=True
            print('Sold {0} {1}'.format(amount_to_sell, coin))
        except:
            amount_to_sell=round(amount_to_sell*0.9975, 6)
    return amount_to_sell

def decision_short(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision = 'hold'

    if current_price > top_price:
        decision = 'buy'

    elif current_price < bot_price:
        bot_price = current_price

    elif current_price > (reference_price-abs((reference_price-bot_price))*0.5) and current_price < reference_price*(1 - minimum_gain):
        decision = 'buy'

    return decision, top_price, bot_price


def decision_long(
    minimum_gain,
    reference_price,
    current_price,
    top_price,
    bot_price,
    ):

    decision='hold'

    if current_price<bot_price:
        decision='sell'

    elif current_price>top_price:
        top_price=current_price

    elif current_price<(reference_price+abs((reference_price-top_price))*0.5) and current_price>reference_price*(1+minimum_gain):
        decision='sell'

    return decision, top_price, bot_price


def dynamic_stoploss_strategy(
    trading_client,
    coin,
    bot_status_json_path,
    current_price,
    pct_gap,
    minimum_gain,
    reinvest_gap=0.8
    ):

    with open(bot_status_json_path) as json_file:
        binance_bot_status = json.load(json_file)

    current_bot_status = binance_bot_status[coin]

    reference_price = current_bot_status['reference_price']
    top_price = current_bot_status['top_price']
    bot_price = current_bot_status['bot_price']

    if current_bot_status['btc'] == 0:  # less than 5 euro
        decision_strategy = decision_long
    else:
        decision_strategy = decision_short


    position, top_price, bot_price = decision_strategy(
        current_price=current_price,
        minimum_gain=minimum_gain,
        reference_price=current_bot_status['reference_price'],
        top_price=current_bot_status['top_price'],
        bot_price=current_bot_status['bot_price'],
        )
    print('Current position: {}'.format(position))

    if position == 'buy':
        buy_all_with_btc(trading_client=trading_client, coin=coin, btc_quantity=current_bot_status['btc'])
        current_bot_status['btc'] = 0
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif position == 'sell':
        current_bot_status['btc'] = sell_all_for_btc(trading_client=trading_client, coin=coin)
        reference_price = current_price
        bot_price = reference_price*(1-minimum_gain)
        top_price = reference_price*(1+pct_gap)

    # reinvest?
    elif current_price > reference_price*(1+reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1-pct_gap)
        top_price = reference_price*(1+minimum_gain)

    elif current_price < reference_price*(1-reinvest_gap):
        reference_price = current_price
        bot_price = reference_price*(1+pct_gap)
        top_price = reference_price*(1-minimum_gain)

    current_bot_status['reference_price'] = reference_price
    current_bot_status['top_price'] = top_price
    current_bot_status['bot_price'] = bot_price

    bot_status_file = bot_status_json_path

    binance_bot_status[coin] = current_bot_status

    with open(bot_status_file, 'w') as f:
        json.dump(binance_bot_status, f)

if __name__=='__main__':
    from binance.client import Client
    from pprint import pprint

    api_key='QuJSzBd0O8Uube4sOr1DOySMsZWsKC5EpjFYP12FZPO0WEQbBrjjU8N5kVPb5Qkt'
    api_secret = 'XiPd9cc3VHDl5sa0juCYs27kVPipPEMkddmHxYol6pGuOWgLsZK4cH7SwpJf4Qev'
    client = Client(api_key, api_secret)
    all_tickers = client.get_all_tickers()
    price_list = {}
    for pair in client.get_all_tickers():
        price_list[pair['symbol']] = float(pair['price'])
    pprint(price_list)
    # pprint(client.get_all_tickers())