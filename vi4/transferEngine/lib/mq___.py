#!/usr/bin/env python3.6
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import logging
from sys import exit
import sys
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG,
    filename='transfers.log')

sys.path.insert(0, './lib')
import transferlib_ as tWrap
import config as conf
DEBUG = True

mq_subtop = 'transfers/incoming'
mq_pubtop = 'messages'

# This is the Publisher


def mqpub(msg):
    client = mqtt.Client(client_id="fund_managemer", clean_session=False)
    client = mqtt.Client('fundbot')
    #client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect(conf.mq_host, conf.mq_port, 60)
    if DEBUG:
        print(msg)
    logging.info(msg)
    #client.publish(mq_pubtop, str(msg))
    publish.single(
        conf.mq_pubtop,
        payload=str(msg),
        hostname=conf.mq_host,
        port=conf.mq_port,
        auth={
            'username': conf.mq_user,
            'password': conf.mq_pass})


def on_connect(client, userdata, flags, rc):
    print("[*] Connected with result code " + str(rc))
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
    if DEBUG:
        print(msg)
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
    # if currency == 'XRP': return False
    # if currency == 'XLM': return False
    # if currency == 'STR': return False
    # if currency == 'XMR': return False
    try:
        _from = obj['from']
    except KeyError:
        pass
    try:
        to = obj['to']
    except KeyError:
        mqpub('Invalid request, key "to" is required')
        return False

    mqpub('Action: %s , Currency: %s, Amount: %s, From: %s, To: %s ' %
          (action, currency, amount, _from, to))
    if action == 'transfer' and (_from == 'bittrex' or _from ==
                                 'poloniex') and currency != 'XLM' and currency != 'STR' and currency != 'XRP' and currency != 'XMR':
        if currency == 'XRP' or 'currency' == 'STR' or currency == 'XLM' or currency == 'XMR':
            mqpub('Logic Error')
            return False
        mqpub('Standard withdrawal requested')
        if to == _from:
            mqpub('Invalid request. From cannot match to.')
            return False
        if float(amount) <= 0:
            mqpub("Invalid request. Amount cannot be nothing")
        _address = tWrap.deposit_address(to, currency)
        if DEBUG:
            print("[*] " + _address)
        logging.info('Address:' + str(_address))
        ret = tWrap._withdraw('0', _from, currency, amount, _address)
        logging.info(ret)
        mqpub(ret)
    else:
        if action == 'transfer' and currency == 'XRP' and float(
                amount) >= float(20.0):
            mqpub('XRP Withdrawal requested')
            if _from == 'bittrex':
                if to == 'bittrex':
                    _address = 'rPVMhWBsfF9iMXYj3aAzJVkPDTFNSyWdKy'
                    payment_id = '129870702'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                if to == 'cex':
                    _address = 'rE1sdh25BJQ3qFwngiTBwaq3zPGGYcrjp1'
                    payment_id = '36930'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                if to == 'poloniex':
                    _address = 'r2CH9EgsVYDm65cJNCXT24FQoe8batovL'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                logging.info(ret)
        elif action == 'transfer' and currency == 'XLM' or currency == 'STR':
            mqpub("XLM withdrawal requested")
            if (_from == 'bittrex') or (_from == 'poloniex'):
                print('Ok')
                if to == 'poloniex':
                    _address = 'GCGNWKCJ3KHRLPM3TM6N7D3W5YKDJFL6A2YCXFXNMRTZ4Q66MEMZ6FI2'
                    payment_id = '5634603'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    logging.info(ret)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                elif to == 'bittrex':
                    _address = 'GB6YPGW5JFMMP2QB2USQ33EUWTXVL4ZT5ITUNCY3YKVWOJPP57CANOF3'
                    payment_id = '3dfd4b15535a420db86'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                elif to == 'cex':
                    _address = 'GB3RMPTL47E4ULVANHBNCXSXM2ZA5JFY5ISDRERPCXNJUDEO73QFZUNK'
                    payment_id = '3110099791642624'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    # return False
                    logging.info(ret)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
        elif action == 'transfer' and currency == 'XMR':
            mqpub(
                '[!] Warn: New XMR Withdrawal functionality requested. Please monitor closely for success.')
            mqpub('[*] XMR Withdrawl requested')
            if (_from == 'bittrex') or (_from == 'poloniex'):
                print('Ok')
                if to == 'poloniex':
                    _address = '4JUdGzvrMFDWrUUwY3toJATSeNwjn54LkCnKBPRzDuhzi5vSepHfUckJNxRL2gjkNrSqtCoRUrEDAgRwsQvVCjZbRwXLvboWTD8V9ChTMG'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address)
                    logging.info(ret)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                elif to == 'bittrex':
                    _address = '463tWEBn5XZJSxLU6uLQnQ2iY9xuNcDbjLSjkn3XAXHCbLrTTErJrBWYgHJQyrCwkNgYvyV3z8zctJLPCZy24jvb3NiTcTJ'
                    payment_id = 'c2b7f53ceace45898a49e04af576ba2d5b324f198d2f4439acae3a81adffa50a'
                    ret = tWrap._withdraw(
                        '0', _from, currency, amount, _address, payment_id)
                    mqpub("DEBUG: Transfer Engine:" + str(ret))
                elif to == 'cex':
                    ret = str(
                        '[!] Warning! XMR Withdrawal requested to cex, cex does NOT support XMR. Not processing.')
                    mqpub('DEBUG: Transfer Engine ' + str(ret))
                    logging.info(ret)
                    return False

        elif action == 'address':
            _address = tWrap.deposit_address(to, currency)
            logging.info(ret)
            mqpub("DEBUG: Transfer Engine:" + str(ret))
        elif action == 'check':
            logging.info('Action check: not implemented')
        elif action == 'test':
            mqpub('[*] DEBUG: Transfer Engine test message.')


def subscribe():
    print('[*] Connecting...')
    client = mqtt.Client('worker_bot')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("127.0.0.1", 1883, 60)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("[!] Caught Signal, exiting...\nBye!")
        logging.info('Program exit')
        client.disconnect()
        sys.exit(0)
    else:
        mqpub('[*] Transfer engine started and awaiting orders.')
