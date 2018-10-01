#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import time
import bittrex as BittrexAPI
import paho.mqtt.client as mqtt
import config

topic = "bbal2"
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(
    config.mq_host,
    port=config.mq_port,
    keepalive=config.mq_keepalive,
    bind_address=config.mq_bindAddress)
client.loop_start()

bit = BittrexAPI.bittrex(config.bittrexKey, config.bittrexSecret)

while True:
    result = {}
    bprice = {}
    try:
        for val in bit.getmarketsummaries().get("result", []):
            key = val.get("MarketName", False)
            if key:
                value = val.get("Bid", 0)
                bprice[key.replace('BTC-', '')] = value

        time.sleep(1)

        bbal = bit.getbalances().get("result", [])
        for val in bbal:
            key = val.get("Currency", False)
            if key:
                available = val.get("Available", 0.0)
                balance = val.get("Balance", 0.0)
                pending = val.get("Pending", 0.0) + balance - available
                value = balance if key == "BTC" else bprice.get(
                    key, 0.0) * balance
                result[key] = {
                    "available": available,
                    "pending": pending,
                    "value": value,
                }
        print(result)
        client.publish(topic, payload=json.dumps(result), qos=0, retain=False)
    except Exception as err:
        print("ERROR", err)
        pass
    time.sleep(config.interval)
