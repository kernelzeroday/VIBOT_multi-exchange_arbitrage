#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Exchange CLI Tool Skeleton
# DarkerEgo 2018


import sys
import json
import logging
from sys import exit

import json
import time
import config
import bittrex as BittrexAPI
import paho.mqtt.client as mqtt


from binance.client import Client

import binconf


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


api_key = binconf.api_key
api_secret = binconf.api_secret
api = Client(api_key, api_secret)


topic = "binbal2"
client = mqtt.Client(topic + "client", clean_session=False)
client.username_pw_set(config.mq_user, config.mq_pass)
client.connect(
    config.mq_host,
    port=config.mq_port,
    keepalive=config.mq_keepalive,
    bind_address=config.mq_bindAddress)
client.loop_start()


def main():

    def get_balances():

        try:
            prebals = api.get_account()['balances']
            bals = {}
            tickers = api.get_all_tickers()
            tickers = json.dumps(tickers)
            tickers = json.loads(tickers)
            for i in range(0, len(prebals)):
                bals[prebals[i]['asset']] = {}
                bals[prebals[i]['asset']]['available'] = prebals[i]['free']
                bals[prebals[i]['asset']]['pending'] = prebals[i]['locked']
                #bals[prebals[i]['asset']]['total'] = float(prebals[i]['free']) + float(prebals[i]['locked'])

                base = (prebals[i]['asset'])
                if base != 'BTC':
                    print(base + "\n")
                    pair = (prebals[i]['asset'] + 'BTC')
                    #total = bals(prebals[i]['asset']['total'])
                    #print(pair+ ' '+total)
                    for i in tickers:
                        if i['symbol'] == pair:
                            price = (i['price'])
                    bals[prebals[i]['asset']]['value'] = float(
                        prebals[i]['free']) + float(prebals[i]['locked']) * float(price)
                else:
                    bals[prebals[i]['asset']]['value'] = float(
                        prebals[i]['free']) + float(prebals[i]['locked'])

                    # print(price)
                    #value = float(price) * float(total)
                    #print('Value: '+pair+' : '+str(value))
                    # ticker = tickers['
                    #value = float(bals[prebals[i]['asset']]['total']) * float(ticker)
                    # print(value)

        except Exception as err:
            logging.error(err)
            eprint('Error getting balances ' + str(err))
            return False
        else:
            #bals = json.dumps(bals)
            return bals

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
