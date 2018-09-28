#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import time
import paho.mqtt.client as mqtt
import config
import requests
import datetime	

#CURRENCIES = ["BTC", "XRP", "ETH", "DASH", "ZEC", "XLM", "STR", "LTC", "ETC", "XMR", "LSK", "GNT", "OMG", "XEM", "ZRX", "SC", "REP", "CVC", "FCT"]
CURRENCIES = ["BTC", "XRP", "ETH", "DASH", "ZEC", "XLM", "STR", "XMR", "LTC"]
usdt = False
verbose = False
# Policy requested by Kaito:
#DASH/BTC, ETH/BTC, XMR/BTC, XLM/BTC, XRP/BTC, ZEC/BTC

SUBSCRIPTIONS = [("pbal2", 0), ("cbal2", 0), ("bbal2", 0), ("binbal2", 0), ('okbal2', 0)]
BITTREX = {}
CEX = {}
POLONIEX = {}
BINANCE = {}
OKEX = {}
log_filename = ""

# Ugly Json Hack
from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle

class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_python_object': b64encode(pickle.dumps(obj)).decode('utf-8')}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(b64decode(dct['_python_object'].encode('utf-8')))
    return dct

def mqpub(msg,topic='messages'):
    client = mqtt.Client(client_id="publish_test", clean_session=False)
    client = mqtt.Client('tester')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("localhost",1883,60)
    client.publish(topic, str(msg));
    client.publish('balance', str(msg));
    client.disconnect();



def lprint(data,topic='messages'):
    global log_filename

    mqpub(data,topic)
    current_date_str = str(datetime.datetime.now().date())

    if log_filename != current_date_str:
        log_filename = current_date_str

    with open('/var/www/html/' + log_filename + '.log', 'a') as f:
        f.write(data+"\n") 


def mqParse(client, userdata, message):
    global BITTREX
    global CEX
    global POLONIEX
    global BINANCE
    global OKEX
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
        elif message.topic == "binbal2":
            BINANCE = res
        elif message.topic == 'okbal2':
            OKEX = res

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
    current_datetime = datetime.datetime.now()
    lprint(str(current_datetime)[:19] + ' UTC')
    lprint("BITTREX")
    bTotal = 0
    for key, val in BITTREX.items():
        if key in CURRENCIES:
            bTotal += val.get("value", 0)
            lprint(str(key)+ " "+str(val))
        if key in 'USDT':
            val = val['available']
            value = requests.get('https://bittrex.com/api/v1.1/public/getticker?market=USDT-BTC')
            value = value.content
            #value = json.dumps(value,cls=PythonObjectEncoder)
            value = json.loads(value,object_hook=as_python_object)
            if usdt:
                if verbose: print(value)
            try:
                value = value['result']['Ask']
                value = float(value)
            except:
                pass
            #print(val / value)
            try:
                bTotal += (float((val) / float(value)))
            except:
                pass
    lprint("BITTREX TOTAL: %f\n" % bTotal)
    mqpub("""{'bittrexTotal':'%f'}""" % (bTotal), 'totalBal')



    binTotal = 0
    lprint("BINANCE")
    for key, val in BINANCE.items():
        if key in CURRENCIES:
            if key == 'BTC':
                binTotal +=val.get('available')
                binTotal +=val.get('pending')
            binTotal += val.get("value", 0)
            lprint(str(key) + " " +str(val))
    lprint("BINANCE TOTAL: '%f'\n" % binTotal)
    mqpub("""{'binanceTotal':'%f'}""" % (binTotal), 'totalBal')

    lprint('OKEX')
    okTotal = 0
    for key,val in OKEX.items():
        if key in CURRENCIES:
            if key == 'BTC':
                okTotal += val.get("available", 0)
                okTotal += val.get("pending", 0)
            okTotal += val.get("value", 0)
            lprint(str(key) + " " +str(val))
    lprint("OKEX TOTAL: '%f'\n" % okTotal)
    mqpub("""{'okexTotal':'%f'}""" % (okTotal), 'totalBal')



    lprint("CEX")
    cTotal = 0
    for key, val in CEX.items():
        if key in CURRENCIES:
            cTotal += val.get("value", 0)
            lprint(str(key) + " " + str(val))
    lprint("CEX TOTAL: %f\n" % cTotal)
    mqpub("""{'cexTotal':'%f'}""" % (cTotal), 'totalBal')
    lprint("POLONIEX")
    pTotal = 0
    for key, val in POLONIEX.items():
        if key in CURRENCIES:
            pTotal += val.get("value", 0)
            lprint(str(key) + " " + str(val))
        #if key in 'USDT':
        #    val = val['value']
        #    pTotal += val
            #value = requests.get('https://poloniex.com/public?command=returnTicker')
            #value = json.loads(value.content)
            #value = value['highestBid']
            #pTotal += (float(val) / float(value))
    lprint("POLONIEX TOTAL: %f\n" % pTotal)
    mqpub("""{'poloniexTotal':'%f'}""" % (pTotal), 'totalBal')
    netTotal = (cTotal + pTotal + bTotal + binTotal + okTotal)
    lprint("TOTAL BTC: %f\n" % (netTotal))
    #mqpub(json.dumps({'net': netTotal}, sort_keys=True), 'balance/net')
    mqpub(netTotal,'balance/net')
    print('Net BTC Value: '+str(netTotal))
    time.sleep(10)
