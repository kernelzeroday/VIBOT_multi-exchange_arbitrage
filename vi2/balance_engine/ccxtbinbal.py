#!/usr/bin/env python3.6
import ccxt
import json
import time
binance = ccxt.binance()

binance.apiKey = 'vURW3wM0yC7vD4RwAZIEFbMsDND5SIXIj0lGWhcv4RlNVlXtk0EVV3bSq9xrC8Jh'
binance.secret = 'r0XkzQBMC6xHXTz7IE9DF9yHmwqWBsuul3lJlX6TfT8YCqqYViItBSdtEkBdZ539'



#print(balance)
#x = input('')
while True:
    balance = binance.fetch_balance()
    tickers = binance.fetch_tickers() 
    ob = {}
    for i in binance.currencies:
      #print(i);print
      try:
        ob[i] = {}
        ob[i]['available'] = balance[i]['free']
        ob[i]['pending'] = balance[i]['used']
        ob[i]['value'] = balance[i]['total'] * tickers[i+'/BTC']['bid']
      except:
        pass

    print(ob)
    time.sleep(2.5)

