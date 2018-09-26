#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import time
import paho.mqtt.client as mqtt
import config

CURRENCIES = ["BTC", "XRP", "ETH", "DASH", "ZEC", "XLM", "STR", "LTC", "ETC", "XMR", "LSK"]
SUBSCRIPTIONS = [("pbal2", 0), ("cbal2", 0), ("bbal2", 0)]
BITTREX = {}
CEX = {}
POLONIEX = {}

def mqParse(client, userdata, message):
    global BITTREX
    global CEX
    global POLONIEX
    try:
        res = json.loads(message.payload)
    except json.JSONDecodeError:
        pass
    else:
        if message.topic == "bbal2":
            BITTREX = res
        elif message.topic == "cbal2":
            CEX = res
        elif message.topic == "pbal2":
            POLONIEX = res

client = mqtt.Client("calc", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
# Event Handlers
client.on_message = mqParse
# Connect to Broker
client.connect(config.mq_host, port=config.mq_port,
               keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
# Subscribe to Topics
client.subscribe(SUBSCRIPTIONS)
client.loop_start()

while 1:
    print("BITTREX")
    bTotal = 0
    for key, val in BITTREX.items():
        if key in CURRENCIES:
            bTotal += val.get("value", 0)
            print(key, val)
    print("BITTREX TOTAL: %f\n" % bTotal)

    print("CEX")
    cTotal = 0
    for key, val in CEX.items():
        if key in CURRENCIES:
            cTotal += val.get("value", 0)
            print(key, val)
    print("CEX TOTAL: %f\n" % cTotal)

    print("POLONIEX")
    pTotal = 0
    for key, val in POLONIEX.items():
        if key in CURRENCIES:
            pTotal += val.get("value", 0)
            print(key, val)
    print("POLONIEX TOTAL: %f\n" % pTotal)

    print("TOTAL BTC: %f\n" % (bTotal + cTotal + pTotal))
    time.sleep(2)

