#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import poloniex as PoloniexAPI
import json
import time
import config
import paho.mqtt.client as mqtt

topic = "pbal2"
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(
    config.mq_host,
    port=config.mq_port,
    keepalive=config.mq_keepalive,
    bind_address=config.mq_bindAddress)
client.loop_start()

pol = PoloniexAPI.Poloniex(config.poloniexKey, config.poloniexSecret)

while True:
    result = {}
    pbal = pol.returnCompleteBalances()
    try:
        print(pbal)
        for key, val in pbal.items():
            available = float(val.get("available", "0.0"))
            pending = float(val.get("onOrders", "0.0"))
            value = float(val.get("btcValue", "0.0"))
            result[key] = {
                "available": available,
                "pending": pending,
                "value": value
            }
        print(result)
        client.publish(topic, payload=json.dumps(result), qos=0, retain=False)
    except BaseException:
        pass
    time.sleep(10)
