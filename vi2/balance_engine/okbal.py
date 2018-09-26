#!/usr/bin/env python3.6
import ccxt
import json
import time
import paho.mqtt.client as mqtt
import config

topic = 'okbal2'
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(config.mq_host, port=config.mq_port,
               keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
client.loop_start()


okex = ccxt.okex()

okex.apiKey = '77f7bb10-6ae4-44c6-8eeb-9710a5fa86d8'
okex.secret = '3E0BA281918F51897158E1B1D10B6D70'


def get_balances():
  #while True:
      balance = okex.fetch_balance()
      tickers = okex.fetch_tickers() 
      ob = {}
      for i in okex.currencies:
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
