#!/usr/bin/env python3.6
import ccxt
import json
import time
import paho.mqtt.client as mqtt
import config

topic = 'binbal2'
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(config.mq_host, port=config.mq_port,
               keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
client.loop_start()


binance = ccxt.binance()

binance.apiKey = 'vURW3wM0yC7vD4RwAZIEFbMsDND5SIXIj0lGWhcv4RlNVlXtk0EVV3bSq9xrC8Jh'
binance.secret = 'r0XkzQBMC6xHXTz7IE9DF9yHmwqWBsuul3lJlX6TfT8YCqqYViItBSdtEkBdZ539'


def get_balances():
  #while True:
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

      return(ob)


def main():

    while 1:
        try:
            res = get_balances()
            print(res)
        except Exception as err:
            print(err)
            pass
        try:
            client.publish(topic, payload=json.dumps(res), qos=0, retain=False)
        except Exception as err:
            print(err)
            pass
        time.sleep(config.interval)

main()
