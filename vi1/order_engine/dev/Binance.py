import sys
import json
import argparse
import logging
import os
from sys import exit
from binance.client import Client

# Log Formatter
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG,
    filename='tool.log')


class Binance(object):
    def __init__(self, k, s):
        self.api = Client(k, s)

    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def get_ticker(self, pair):
        pair = str(pair)
        if pair == 'null':
            self.eprint('WARN: No pair specified, defaulting to BTC-ETH')
            pair == 'BTC-ETH'
        try:
            t = self.api.get_recent_trades(symbol=pair)
        except Exception as err:
            logging.error(err)
            self.eprint('Error getting ticker data: ' + str(err))
            return False
        else:
            tt = json.dumps(t)
            #tt = json.loads(tt)
            try:
                #tt = tt['Last']
                return(tt)
            except Exception as err:
                self.eprint(err)
                # return(tt)

    def get_deposit_address(self, currency):
        if currency == 'null':
            self.eprint('WARN: No currency specified, defaulting to BTC')
            currency = 'BTC'
        try:
            add = self.api.get_deposit_address(asset=currency)
        except Exception as err:
            logging.error(err)
            self.eprint("Error getting deposit address: " + str(err))
            return False
        else:
            add_ = json.dumps(add)
            return add_

    def get_balances(self):
        try:
            bals = self.api.get_account()['balances']
        except Exception as err:
            logging.error(err)
            self.eprint('Error getting balances' + str(err))
            return False
        else:
            bals = json.dumps(bals)
            return bals

    def get_balance(self, currency):
        if currency == 'null':
            self.eprint('WARN: No currency specified, defaulting to BTC')
            currency = 'BTC'
        try:
            bal = self.api.get_asset_balance(currency)
        except Exception as err:
            logging.info(err)
            self.eprint('Error getting balance' + str(err))
            return False
        else:
            bal = json.dumps(bal)
            return bal

    def get_order_book(self, pair, otype, depth=20):
        pair = str(pair)
        otype = str(otype)
        depth = int(depth)
        try:
            ret = self.api.get_order_book(symbol=pair)
        except Exception as err:
            self.eprint("Error getting orderbook")
            logging.info("Error getting orderbook: " + str(err))
        else:
            ret = json.dumps(ret)
            return ret

    def buy_limit_order(self, pair, amount, price):
        if pair == 'null':
            self.eprint('Specify a pair with -p')
            return False
        if amount == '0.0':
            self.eprint('Specify an amount with -a')
            return False
        if price == '0.0':
            self.eprint('Specify a price with -P')
            return False
        try:
            ret = self.api.order_market_buy(
                symbol=pair, quantity=amount, price=price)
        except Exception as err:
            logging.info(err)
            self.eprint('Error placing buy limit order: ' + str(err))
            return False
        else:
            ret = json.dumps(ret)
            return(ret)

    def sell_limit_order(self, pair, amount, price):
        if pair == 'null':
            self.eprint('Specify a pair with -p')
            return False
        if amount == '0.0':
            self.eprint('Specify an amount with -a')
            return False
        if price == '0.0':
            self.eprint('Specify a price with -P')
            return False
        try:
            ret = self.api.order_market_sell(
                symbol=pair, quantity=amount, price=price)
        except Exception as err:
            logging.info(err)
            self.eprint('Error placing sell limit order: ' + str(err))
            return False
        else:
            ret = json.dumps(ret)
            return(ret)

    def buy_market_order(self, pair, amount):
        if pair == 'null':
            self.eprint('Specify a pair with -p')
            return False
        if amount == '0.0':
            self.eprint('Specify an amount with -a')
            return False
        try:
            ret = self.api.order_market_buy(symbol=pair, quantity=amount)
        except Exception as err:
            self.eprint(err)
            logging.info(err)
        else:
            try:
                ret = json.dumps(ret)
            except Exception as err:
                logging.info(err)
            else:
                return(ret)

    def sell_market_order(self, pair, amount):
        if pair == 'null':
            self.eprint('Specify a pair with -p')
            return False
        if amount == '0.0':
            self.eprint('Specify an amount with -a')
            return False
        try:
            ret = self.api.order_market_sell(symbol=pair, quantity=amount)
        except Exception as err:
            self.eprint(err)
            logging.info(err)
        else:
            try:
                ret = json.dumps(ret)
            except Exception as err:
                logging.info(err)
            else:
                return(ret)

    def cancel(self, order_id, pair):
        if order_id == 'null':
            self.eprint('Specify an order_id with -i')
            return False
        try:
            ret = self.api.cancel_order(orderId=order_id, symbol=pair)
        except Exception as err:
            logging.info(err)
            self.eprint('Error canceling order: ' + str(err))
            return False
        else:
            ret = json.dumps(ret)
            return(ret)

    def do_withdraw(self, currency, amount, address):
        if currency == 'null':
            self.eprint('Specify a currency with -c !')
            return False
        if amount == '0.0':
            self.eprint('Specify an amount with -a !')
            return False
        if address == 'null':
            self.eprint('Specify an address with -A !')
            return False
        print('Please review the following information carefully!')
        print('Currency: ' + str(currency))
        print('Address: ' + str(address))
        print('Amount: ' + str(amount))
        do_it = input("Proceed? (YES/NO) :")
        if do_it == 'YES':
            try:
                ret = self.api.withdraw(
                    asset=currency, address=address, amount=amount)
            except Exception as err:
                logging.error(err)
                self.eprint('Error withdrawing currency: ' + str(err))
                return False
            else:
                ret = json.dumps(ret)
                return(ret)
        else:
            return(str('Withdrawal canceled'))
            logging.info('Function: do_withdraw : Withdrawal canceled')
            return False

    def wd_history(self, currency, count=10):
        if currency == 'null':
            #self.eprint('No currency specified, defaulting to BTC')
            currency = ''
        try:
            ret = self.api.get_withdraw_history(asset=currency)
        except Exception as err:
            logging.info(err)
            self.eprint('Error getting wd history: ' + str(err))
        else:
            ret = json.dumps(ret)
            return(ret)

    def get_orders(self, pair):
        if pair == 'null':
            pair = ''
        try:
            ret = self.api.get_open_orders(symbol=pair)
        except Exception as err:
            logging.info(err)
            self.eprint('Error getting open orders: ' + str(err))
        else:
            ret = json.dumps(ret)
            return(ret)

    def getcurrencies(self):
        try:
            ret = self.api.getcurrencies()
        except Exception as err:
            logging.info(err)
            self.eprint('Error getting currency data' + str(err))
        else:
            ret = json.dumps(ret)
            print(ret)

    def deposithistory(self, currency, count=10):
        if currency == 'null':
            currency = ''
        try:
            ret = self.api.get_deposit_history(asset=currency)
        except Exception as err:
            logging.info(err)
            self.eprint('Error getting deposit history' + str(err))
        else:
            ret = json.dumps(ret)
            print(ret)

    def orderHist(self, pair, count=10):
        if pair == 'null':
            pair = ''
        try:
            ret = self.api.get_all_orders(symbol=pair, limit=count)
        except Exception as err:
            logging.info(err)
        else:
            ret = json.dumps(pair)
            print(ret)

    def query_order(self, order_id):
        if order_id == 'null':
            self.eprint('Specify an order id (uuid) with -i')
            return False
        else:
            try:
                ret = self.api.get_order(symbol=pair, orderId=order_id)
            except Exception as err:
                self.eprint('Error getting order history: ' + str(err))
                return False
            else:
                ret = json.dumps(ret)
                return(ret)
