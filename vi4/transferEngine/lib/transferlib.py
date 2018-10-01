#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Anon 2018
# Exchange withdrawal Modular Functions
""" Modular Libary for automated withdrawals & deposits """

# import libaries
import json
import sys
import time
import poloniex
import logging
import optparse
import sys
# Required to Serialize Json
from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle
# local libs
import bittrex  # TODO: update to v2 api
import config
import cex  # custom modified version of python-cexio
# define exchanges
wdex = str('poloniex bittrex')
dpex = str('cex poloniex bittrex')
proceed = 'YES'
# log formatting
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG,
    filename='transfers.log')

# Modular Class to Serialize Json


def debug():
    return False


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_python_object': b64encode(pickle.dumps(obj)).decode('utf-8')}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(b64decode(dct['_python_object'].encode('utf-8')))
    return dct

# print to stderr


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
# generate a time stamp


def tS():
    return time.time()

# do a withdrawal - nested functions


def _withdraw(live, exchange, currency, amount, address, payment_id=None):

    def bittrex_withdraw(live, currency, amount, address, payment_id=None):
        bittrexAPI = bittrex.bittrex(config.bittrexKey, config.bittrexSecret)
        logging.info('Bittrex Withdrawal call initiated')
        if not currency:
            return False
        if not amount:
            return False
        if not address:
            return False
        if payment_id and live == '0':
            if debug:
                print('[!] Warning: attempting new payment id functionality...')
            try:
                ret = bittrexAPI.withdraw(
                    currency, amount, address, payment_id)
            except Exception as err:
                logging.error(err)
                eprint('Error withdrawing currency: ' + str(err))
            else:
                ret = json.dumps(ret)
                print(ret)
                return('INFO:' + str(tS) + ' Withdrawal: ' + str(ret))

        elif not payment_id and live == '0':
            try:
                ret = bittrexAPI.withdraw(currency, amount, address)
            except Exception as err:
                logging.error(err)
                eprint('Error withdrawing currency: ' + str(err))
                return False
            else:
                ret = json.dumps(ret)
                print(ret)
                return('INFO:' + str(tS) + ' Withdrawal: ' + str(ret))
        else:
            return(str('Canceled Withdrawal of currency: %s , amount: %s to address: %s ') % (currency, amount, address))
            logging.info('Function: do_withdraw : Withdrawal canceled')

    def poloniex_withdraw(live, currency, amount, address, payment_id=None):
        poloniexAPI = poloniex.Poloniex(
            config.poloniexKey, config.poloniexSecret)
        logging.info('Poloniex withdrawal call initiated')
        if not currency:
            return False
        if not amount:
            return False
        if not address:
            return False
        if currency == 'XLM':
            currency = 'STR'
        if live == '0':
            try:
                if payment_id:
                    ret = poloniexAPI.withdraw(
                        currency, amount, address, payment_id)
                else:
                    ret = poloniexAPI.withdraw(currency, amount, address)
            except Exception as seriouserror:
                logging.info('Error withdrawing!' + str(seriouserror))
            else:
                ret = json.dumps(ret, cls=PythonObjectEncoder)
                print(ret)
                return('INFO:' + str(tS) + ' Withdrawal: ' + str(ret))

        else:
            if payment_id:
                return('Canceling poloniex withdrawl of curreny: %s amount %s to address %s , payment_id: %s' % (currency, amount, address, payment_id))
            else:
                return('Canceling poloniex withdrawl of curreny: %s amount %s to address %s' % (currency, amount, address))

    if payment_id:
        if exchange == 'poloniex':
            poloniex_withdraw(live, currency, amount, address, payment_id)
        if exchange == 'bittrex':
            bittrex_withdraw(live, currency, amount, address, payment_id)
    else:
        if exchange == 'poloniex':
            poloniex_withdraw(live, currency, amount, address)
        if exchange == 'bittrex':
            bittrex_withdraw(live, currency, amount, address)

    print('Currency:' + str(currency))
    print('Amount :' + str(amount))
    print('Address: ' + str(address))
    if payment_id:
        print('INFO: Payment id %s specified' % payment_id)

# get deposit addresses - nested functions


def deposit_address(exchange, currency):

    def poloniex_address(currency):
        poloniexAPI = poloniex.Poloniex(
            config.poloniexKey, config.poloniexSecret)
        logging.info('Get deposit address call')
        try:
            ret = poloniexAPI.returnDepositAddresses()
        except Exception as err:
            logging.info(err)
            eprint("Error getting deposit address: " + str(err))
        else:
            ret = json.dumps(ret, cls=PythonObjectEncoder)
            ret = json.loads(ret, object_hook=as_python_object)
            try:
                ret = ret[currency]
            except KeyError as err:
                eprint('Key error' + str(err))
            return(ret)

    def bittrex_address(currency):
        bittrexAPI = bittrex.bittrex(config.bittrexKey, config.bittrexSecret)
        try:
            add = bittrexAPI.getdepositaddress(currency)
        except Exception as err:
            logging.error(err)
            eprint("Error getting deposit address: " + str(err))
            return False
        else:
            add = json.dumps(add)
            add = json.loads(add)
            add = add['Address']
            return add

    def cex_address(currency):
        cexAPI = cex.Api(config.cexUser, config.cexKey, config.cexSecret)
        try:
            add = cexAPI.get_deposit_addresses(currency)
            print(add)
        except Exception as err:
            eprint('Error: ' + str(err))
        else:
            add = json.dumps(add)
            add = json.loads(add)
            add = add['data']
            return add

    if exchange == 'poloniex':
        ret = poloniex_address(currency)
    if exchange == 'bittrex':
        ret = bittrex_address(currency)
    if exchange == 'cex':
        ret = cex_address(currency)
    return(ret)
