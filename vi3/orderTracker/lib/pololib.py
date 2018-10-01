#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import poloniex
import json
import sys
import time
import datetime
import config
debug = True
key = config.poloniexKey
secret = config.poloniexSecret


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


import logging
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG,
    filename='pololib.log')


def eprint(data):
    print(data)


def tS():
    return time.time()


data = poloniex.Poloniex(key, secret)
logging.debug("Program started at %s" % tS)


def ticker(pair):
    ticker = data.returnTicker()
    # this fixes json!
    ret = json.dumps(ticker[pair])
    logging.info("Ticker call: " + ret)
    print(ret)


def move_order(order_id, pair, price, amount):

    if order_id == 'null' or pair == 'null' or float(
            price) <= float('0.0') or float(amount) <= float('0.0'):
        print("Specifiy an order id <-> , price <-P> , pair <-> , and amount <-a>")
        (1)
    else:
        try:
            ret = data.moveOrder(order_id, price, amount)
        except Exception as err:
            logging.info(err)
            print(err)
            return False
        else:
            ret = json.dumps(ret)
            logging.info(ret)
            print(ret)


def all_balance():
    bals = data.returnCompleteBalances('all')
    bret = json.dumps(bals)
    logging.info("All balances call : " + str(bret))
    print(bret)


def balances():
    bal = data.returnCompleteBalances('all')
    ret = json.dumps(bal)
    logging.info("Balance call: " + ret)
    return(ret)


def hist(pair):
    if not pair:
        history = data.returnTradeHistory()
        logging.info("History call. Not logging that much data.")
        for i in history:
            print("%s\n" % i)
    else:
        history = data.returnTradeHistory(pair)
        logging.info("History call. Not logging that much data.")
        for i in history:
            print("%s\n" % i)


def genadd(currency):
    ret = data.generateNewAddress(currency)
    ret = json.dumps(ret)
    logging.info("Generate Deposit address called: " + ret)
    print(ret)


def buy(pair, amount, price):
    if pair != 'null':
        if float(price) > 0.0:
            if float(amount) > 0.0:
                try:
                    ret = data.buy(pair, price, amount)
                    amount = str(amount)
                    price = str(price)
                    logging.info(
                        "Buy order call: %s %s at %s " %
                        (amount, pair, price))
                except Exception as err:
                    print(err)
                    logging.info(err)
                    return False
                else:
                    if debug:
                        print(ret)
                    #ret = json.dumps(ret)
                    #ret_ = str(ret)
                    logging.debug("Buy order call: " + str(ret))
                    #pret = json.loads(ret)
                    _pret = json.dumps(ret, cls=PythonObjectEncoder)
                    pret_ = json.loads(_pret, object_hook=as_python_object)
                    order_id = pret_['orderNumber']
                    order_id = str(order_id)
                    print(ret)
                    return order_id
            else:
                print(buysell_err)
                return False
        else:
            print(buysell_err)
            return False

    else:
        print(buysell_err)
        return False


def sell(pair, amount, price):
    if pair != 'null':
        if float(price) > 0.0:
            if float(amount) > 0.0:
                try:
                    ret = data.sell(pair, price, amount)
                except Exception as err:
                    eprint(err)
                    logging.info(err)
                    return False
                else:
                    #ret = json.dumps(ret)
                    _pret = json.dumps(ret, cls=PythonObjectEncoder)
                    pret_ = json.loads(_pret, object_hook=as_python_object)
                    order_id = pret_['orderNumber']
                    if debug:
                        print(ret)
                    #ret_ = str(ret)
                    price = str(price)
                    amount = str(amount)
                    logging.info(
                        "Sell order call: %s %s at %s " %
                        (amount, pair, price))
                    print(ret)
                    return order_id
            else:
                print(buysell_err)
                return False
        else:
            print(buysell_err)
            return False
    else:
        print(buysell_err)
        return False


def orders():
    try:
        ret = data.returnOpenOrders('all')
    except Exception as err:
        eprint(err)
        return False
    else:
        ret = json.dumps(ret)
        logging.info("Open orders call: " + ret)
        print(ret)


def cancel_order(order_id):
    if order_id != 'null':
        try:
            ret = data.cancelOrder(order_id)
        except Exception as err:
            eprint(err)
            return False
        else:
            ret = json.dumps(ret)
            logging.info("Cancel order call: " + ret)
            print(ret)
    else:
        eprint("Please specify order id with -i <order id>")
        return False


def deposit_addresses():
    logging.info('Get deposit address call')
    try:
        ret = data.returnDepositAddresses()
    except Exception as err:
        logging.info(err)
    else:
        ret = json.dumps(ret)
        print(ret)


def deposit_history():
    timeNow = int(createTimeStamp(
        '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())))
    span = int(timeNow) - int(since)
    try:
        ret = json.dumps(
            data.returnDepositsWithdrawals(
                start=False, end=False))
    except Exception as err:
        logger.info(err)
        print(err)
    else:
        #ret = json.dumps(ret)
        print(ret)


def getfee():
    logging.info('Fee info call initatiated')
    try:
        ret = data.returnFeeInfo()
    except Exception as err:
        eprint(err)
        return False
    else:
        ret = json.dumps(ret)
        print(ret)


def information():
    ret = data.returnCurrencies()
    ret = json.dumps(ret)
    print(ret)


def withdraw(currency, amount, address, payment_id=None):
    logging.info('Withdrawal call initiated')
    if not currency:
        return False
    if not amount:
        return False
    if not address:
        return False
    print('WARNING: Please double check all required info for withdrawal!')
    if payment_id:
        print('INFO: Payment id %s specified' % payment_id)

    print('Currency:' + str(currency))
    print('Amount :' + str(amount))
    print('Address: ' + str(address))

    try:
        confirm = input('Proceed? (YES/NO): ')
        if confirm == 'YES':
            do_wd = True
        else:
            print('Canceling.')
            return False
    except Exception as err:
        logger.info(err)
        return False
    else:
        if do_wd:
            try:
                ret = data.withdraw(currency, amount, address, paymentId=None)
            except Exception as seriouserror:
                logging.info('Error withdrawing!' + str(seriouserror))
            else:
                ts = timeStamp()
                wd_ret = json.dumps(ret)
                print(wd_ret)
                logging.info('INFO:' + str(ts) + ' Withdrawal: ' + str(wd_ret))
