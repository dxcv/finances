# cd /home/pi/finances/finances/

# git checkout hf_data -q

/home/pi/.virtualenvs/finances/bin/python2.7 /home/pi/finances/finances/market/bitstamp_data_collector.py
sleep 30
/home/pi/.virtualenvs/finances/bin/python2.7 /home/pi/finances/finances/market/bitstamp_data_collector.py