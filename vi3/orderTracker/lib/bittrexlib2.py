#!/usr/bin/env/python3.6
import json
import argparse
import logging
from sys import exit
import config as conf
# Log Formatter
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG, filename='blib.log')
# local imports
import bittrex

key = conf.bittrexKey
secret = conf.bittrexSecret
debug=True

def ticker(pair):
    api = bittrex.bittrex(key, secret)
    pair = str(pair)
    if pair == 'null':
        eprint('WARN: No pair specified, defaulting to BTC-ETH')
        pair == 'BTC-ETH'
    try:
        t = api.getticker(pair)
    except Exception as err:
        logging.error(err)
        eprint('Error getting ticker data: '+str(err))
        return False
    else:
        tt = json.dumps(t)
        if debug: print(tt)
        return(tt)

def get_deposit_address(currency):
    api = bittrex.bittrex(key, secret)
    if currency == 'null':
        eprint('WARN: No currency specified, defaulting to BTC')
        currency = 'BTC'
    try:
        add = api.getdepositaddress(currency)
    except Exception as err:
        logging.error(err)
        eprint("Error getting deposit address: "+ str(err))
        return False
    else:
        add_ = json.dumps(add)
        return add_
    
def balances():
    
    api = bittrex.bittrex(key, secret)
    try:
        bals = api.getbalances()
    except Exception as err:
        logging.error(err)
        eprint('Error getting balances' + str(err))
        return False
    else:
        bals = json.dumps(bals)
        return bals
    
def get_balance(currency):
    api = bittrex.bittrex(key, secret)
    if currency == 'null':
        eprint('WARN: No currency specified, defaulting to BTC')
        currency = 'BTC'
    try:
        bal = api.getbalance(currency)
    except Exception as err:
        logging.info(err)
        eprint('Error getting balance' + str(err))
        return False
    else:
        bal = json.dumps(bal)
        return bal

def get_order_book(pair,otype,depth=20):
    api = bittrex.bittrex(key, secret)
    pair = str(pair)
    otype = str(otype)
    depth = int(depth)
    try:
        ret = api.getorderbook(pair, otype, depth)
    except Exception as err:
        eprint("Error getting orderbook")
        logging.info("Error getting orderbook: "+ str(err))
    else:
        ret = json.dumps(ret)
        
        return ret

def buy(pair, amount, price):
    api = bittrex.bittrex(key, secret)
    if pair == 'null':
        eprint('Specify a pair with -p')
        return False
    if amount == '0.0':
        eprint('Specify an amount with -a')
        return False
    if price == '0.0':
        eprint('Specify a price with -P')
        return False
    try:
        ret = api.buylimit(pair, amount, price)
    except Exception as err:
        logging.info(err)
        eprint('Error placing buy limit order: '+ str(err))
        return False
    else:
        #ret = json.dumps(ret)
        #ret = json.loads(ret)
        ret = ret['uuid']
        return(ret)

def sell(pair, amount, price):
    api = bittrex.bittrex(key, secret)
    if pair == 'null':
        eprint('Specify a pair with -p')
        return False
    if amount == '0.0':
        eprint('Specify an amount with -a')
        return False
    if price == '0.0':
        eprint('Specify a price with -P')
        return False
    try:
        ret = api.selllimit(pair, amount, price)
    except Exception as err:
        logging.info(err)
        eprint('Error placing sell limit order: '+ str(err))
        return False
    else:
        ret = json.dumps(ret)
        #ret = json.loads(ret)
        #ret = ret['uuid']

        return(ret)

def buy_market_order(pair, amount):
#
    #
    api = bittrex.bittrex(key, secret)
    if pair == 'null':
        eprint('Specify a pair with -p')
        return False
    if amount == '0.0':
        eprint('Specify an amount with -a')
        return False
    try:
        ret = api.buymarket(pair,amount)
    except Exception as err:
       eprint(err)
       logging.info(err)
    else:
       try:
           ret = json.dumps(ret)
       except Exception as err:
           logging.info(err)
       else:
           return(ret)


def sell_market_order(pair, amount):
    api = bittrex.bittrex(key, secret)
    if pair == 'null':
        eprint('Specify a pair with -p')
        return False
    if amount == '0.0':
        eprint('Specify an amount with -a')
        return False
    try:
        ret = api.sellmarket(pair,amount)
    except Exception as err:
        eprint(err)
        logging.info(err)
    else:
        try:
            ret = json.dumps(ret)
        except Exception as err:
            logging.info(err)
        else:
            return(ret)



def cancel(order_id):
    api = bittrex.bittrex(key, secret)
    if order_id == 'null':
        eprint('Specify an order_id with -i')
        return False
    try:
        ret = api.cancel(order_id)
    except Exception as err:
        logging.info(err)
        eprint('Error canceling order: '+ str(err))
        return False
    else:
        ret = json.dumps(ret)
        return(ret)

def do_withdraw(currency, amount, address):
    api = bittrex.bittrex(key, secret)
    if currency == 'null':
        eprint('Specify a currency with -c !')
        return False
    if amount == '0.0':
        eprint('Specify an amount with -a !')
        return False
    if address == 'null':
        eprint('Specify an address with -A !')
        return False
    print('Please review the following information carefully!')
    print('Currency: ' +str(currency))
    print('Address: ' + str(address))
    print('Amount: ' + str(amount))
    do_it = input("Proceed? (YES/NO) :")
    if do_it == 'YES':
        try:
            ret = api.withdraw(currency, amount, address)
        except Exception as err:
            logging.error(err)
            eprint('Error withdrawing currency: ' + str(err))
            return False
        else:
            ret = json.dumps(ret)
            return(ret)
    else:
        return(str('Withdrawal canceled'))
        logging.info('Function: do_withdraw : Withdrawal canceled')
        return False

def wd_history(currency, count=10):
    api = bittrex.bittrex(key, secret)
    if currency == 'null':
        #eprint('No currency specified, defaulting to BTC')
        currency = ''
    try:
        ret = api.getwithdrawalhistory(currency, count)
    except Exception as err:
        logging.info(err)
        eprint('Error getting wd history: ' + str(err))
    else:
        ret = json.dumps(ret)
        return(ret)
    
def orders(pair):
    api = bittrex.bittrex(key, secret)
    if pair == 'null':
        pair=''
    try:
        ret = api.getopenorders(pair)
    except Exception as err:
        logging.info(err)
        eprint('Error getting open orders: ' + str(err))
    else:
        ret = json.dumps(ret)
        return(ret)

def getcurrencies():
    api =  bittrex.bittrex(key, secret)
    try:
        ret = api.getcurrencies()
    except Exception as err:
        logging.info(err)
        eprint('Error getting currency data'+ str(err))
    else:
        ret = json.dumps(ret)
        print(ret)

def deposithistory(currency,count=10):
    api = bittrex.bittrex(key, secret)

    if currency == 'null':
        currency=''
    
    try:
        ret = api.getdeposithistory(currency,count)
    except Exception as err:
        logging.info(err)
        eprint('Error getting deposit history' +str(err))
    else:
        ret = json.dumps(ret)
        print(ret)

def orderHist(pair,count=10):
    api = bittrex.bittrex(key, secret)
    if pair == 'null' : pair=''
    try:
        ret = api.getorderhistory(pair,count)
    except Exception as err:
        logging.info(err)
    else:
        ret = json.dumps(pair)
        print(ret)

def query_order(order_id):
    api = bittrex.bittrex(key, secret)
    if order_id == 'null':
        eprint('Specify an order id (uuid) with -i')
        return False
    else:
       try:
          ret = api.getorder(order_id)
       except Exception as err:
          eprint('Error getting order history: ' + str(err))
          return False
       else:
          ret = json.dumps(ret)
          return(ret)

