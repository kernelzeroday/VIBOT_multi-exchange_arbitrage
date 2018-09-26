#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import time
import paho.mqtt.client as mqtt
import config

SUBSCRIPTIONS = []
MARKETS = ["BTC_ETH", "BTC_XRP", "BTC_DASH", "BTC_ZEC", "BTC_XLM", "BTC_STR", "BTC_LTC", "BTC_ETC", "BTC_XMR", "BTC_LSK", "ETH_ETC", "ETH_GNT", "ETH_OMG", "ETH_ZEC", "ETH_CVC", "ETH_ZRX", "ETH_SC", "BTC_ZRX"]
EXCHANGES = ["poloniex", "cex", "bittrex"]
for x in MARKETS:
    for i in EXCHANGES:
        SUBSCRIPTIONS+=([('ticker/'+i+'/'+x, 0)])
print(SUBSCRIPTIONS)

def mqParse(client, userdata, msg):
    try:
        
        #res = json.dumps(msg.payload.decode("utf-8"))
        res = str(msg.payload.decode("utf-8"))
    except Exception as err:
        print(err)
        
    else:
        #print(str(msg.topic)+ " : "  +str(res))
        f = str(msg.topic)
        #f.decode("utf-8", "ignore")
        with open(f,'w') as ff:
            #res.decode("utf-8", "ignore")
            ff.write(res)

client = mqtt.Client("tickparser", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
# Event Handlers
client.on_message = mqParse
# Connect to Broker
client.connect(config.mq_host, port=config.mq_port,
               keepalive=60)
# Subscribe to Topics
client.subscribe(SUBSCRIPTIONS)
client.loop_start()

while 1:
    time.sleep(0.1)

