cd /home/hordeus/finances/finances/

git checkout update_data -q

# echo "BTC bot:"
# /home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_btc.py

echo "ETH bot:"
/home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_eth.py

echo "LTC bot:"
/home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_ltc.py

# echo "XRP bot:"
# /home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_xrp.py

# echo "BCH bot:"
# /home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_bch.py