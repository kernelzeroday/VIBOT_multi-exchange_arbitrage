#!/usr/bin/env python3.6
import paho.mqtt.client as mqtt
import json,logging
from sys import exit
import sys
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG, filename='transfers.log')

sys.path.insert(0, './lib')
import transferlib as tWrap

DEBUG=False

mq_subtop='transfers/incoming'
mq_pubtop='transfers/outgoing'

# This is the Publisher
def mqpub(msg):
    client = mqtt.Client(client_id="fund_managemer", clean_session=False)
    client = mqtt.Client('fundbot')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("localhost",1883,60)
    if DEBUG: print(msg)
    logging.info(msg)
    client.publish(mq_pubtop, str(msg))


def on_connect(client, userdata, flags, rc):
  print("[*] Connected with result code "+str(rc))
  client.subscribe(mq_subtop)

def on_message(client, userdata, msg):

    """
    {
    "action": "transfer",
    "amount": "1",
    "currency": "BTC",
    "from": "poloniex",
    "to": "cex"
    }
    """

    if msg.payload.decode() == "quit":
      client.disconnect()
    else:
        msg = msg.payload.decode()
    if DEBUG: print(msg)
    obj = json.loads(msg)
    try:
        action = obj['action']
    except KeyError:
        mqpub('Invalid request, key: action')
        return False
    try:
        amount = obj['amount']
    except KeyError:
        pass
    try:
        currency = obj['currency']
    except KeyError:
        mqpub('Invalid request, key: currency is required')
        return False
    if currency == 'XRP': return False
    if currency == 'XLM': return False
    if currency == 'STR': return False
    if currency == 'XMR': return False
    try:
        _from = obj['from']
    except KeyError:
        pass
    try:
        to = obj['to']
    except KeyError:
        mqpub('Invalid request, key "to" is required')
        return False

    mqpub('Action: %s , Currency: %s, Amount: %s, From: %s, To: %s ' %(action,currency,amount,_from,to))
    if action == 'transfer' and (_from == 'bittrex' or _from == 'poloniex'):
        if to == _from: 
            mqpub('Invalid request. From cannot match to.') 
            return False
        if float(amount) <= 0:
            mqpub("Invalid request. Amount cannot be nothing")
        _address = tWrap.deposit_address(to,currency)
        if DEBUG: print("[*] " + _address)
        logging.info('Address:'+ str(_address))
        ret = tWrap._withdraw('0',_from,currency,amount,_address)
        logging.info(ret)
        mqpub(ret)
    elif action == 'address':
        _address = tWrap.deposit_address(to,currency)
        logging.info(ret)
        mqpub(ret)



def subscribe():
    print('[*] Connecting...')
    client = mqtt.Client('worker_bot')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu') 
    client.connect("127.0.0.1",1883,60)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("[!] Caught Signal, exiting...\nBye!")
        logging.info('Program exit')
        client.disconnect()
        sys.exit(0)
