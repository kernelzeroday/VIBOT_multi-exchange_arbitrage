#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import time
import json
import requests
import paho.mqtt.client as mqtt
import cexio as CexAPI
import config

topic = "cbal2"
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(config.mq_host, port=config.mq_port,
               keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
client.loop_start()


cex = CexAPI.Api(config.cexUser, config.cexKey, config.cexSecret)
# CEX
while 1:
    result = {}
    cprice = {}
    try:
        cvals = requests.post("https://cex.io/api/last_prices/BTC", data=None, headers={'User-agent': 'bot-cex.io-' + cex.username }).json()
        for val in cvals.get("data", []):
            key = val.get("symbol1", False)
            if key:
                cprice[key] = float(val.get("lprice", "0.0"))
        time.sleep(1)

        cbal = cex.balance
        for key, val in cbal.items():
            if isinstance(val, dict):
                available = float(val.get("available", "0.0"))
                pending = float(val.get("orders", "0.0"))
                value = (available + pending) if key == "BTC" else (available + pending) * cprice.get(key, 0.0)

                result[key] = {
                    "available": available,
                    "pending": pending,
                    "value": value,
                }
        print(result)
        client.publish(topic, payload=json.dumps(result), qos=0, retain=False)
    except:
        pass
    time.sleep(config.interval)

