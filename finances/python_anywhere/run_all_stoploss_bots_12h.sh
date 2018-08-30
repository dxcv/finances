cd /home/hordeus/finances/finances/

git checkout update_data -q

echo "Running bots bitstamp:"
/home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_bitstamp.py

echo "Running bots binance:"
/home/hordeus/.virtualenvs/finances/bin/python3.6 /home/hordeus/finances/finances/trading/bots/dynamic_stoploss/run_dynamic_stoploss_bot_binance.py