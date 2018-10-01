#!/usr/bin/env python3.6
import paho.mqtt.client as mqtt
import json
import time
import logging
import optparse
import sys
sys.path.insert(0, './lib')
import transferlib as tWrap

logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG,
    filename='transfers.log')
# Command line args
import mqlib as mq

print('[*] ARGV      :', sys.argv[1:])
parser = optparse.OptionParser()
parser.add_option('-w', '--withdraw',
                  dest="withdraw",
                  action="store_true",
                  default=False,
                  )

parser.add_option('-e', '--exchange',
                  dest="exchange",
                  type="str",
                  # default="bittrex",
                  )

parser.add_option('-d', '--deposit_exchange',
                  dest="deposit_exchange",
                  type="str",
                  )


parser.add_option('-c', '--currency',
                  dest="currency",
                  default="BTC",
                  )

parser.add_option('-q', '--quantity',
                  dest="quantity",
                  default="0.0",
                  type="float",
                  )

parser.add_option('-g', '--get_address',
                  dest="get_address",
                  action="store_true",
                  default=False,
                  )

parser.add_option('-s', '--safe',
                  dest="safe",
                  default=False,
                  action="store_true",
                  )

parser.add_option('-l', '--live',
                  dest="live",
                  default=False,
                  action="store_true",
                  )

parser.add_option('-m', '--mqttd',
                  dest="mqttd",
                  default=False,
                  action="store_true",
                  )


options, remainder = parser.parse_args()

exchange = options.exchange
deposit_exchange = options.deposit_exchange
currency = options.currency
quantity = options.quantity
mqttd = options.mqttd

if not mqttd:
    print('Withdraw Exchange :', exchange)
    print('Deposit Exchange: ', deposit_exchange)
    print('Currency : ', currency)
    print('Quantity:', quantity)

else:
    mq.mqpub('[*] Transfer Engine awaiting orders.')
#print('Verbose   :', options.verbose)
#print('Withdraw    :', options.withdraw)
#print('Deposit to: ', options.deposit_exchange)
#print('Withdraw from :', options.exchange)
#print('Currency : ', options.currency)
#print('Quantity:' ,  options.quantity)
#print('Address:', options.address)
#print('Get Address: ', options.get_address)
#print('Live mode: ', options.live)


if options.live or mqttd:
    print('[!] Warning: live mode enabled!')
    live = '0'
else:
    print('[*] Notice: demo mode, will not actually withdraw.')
    live = '1'

if options.withdraw:
    withdraw = True
    print('Withdrawal requested.')
else:
    withdraw = False

if options.get_address:
    get_address = True
else:
    get_address = False

if options.safe:
    safe = True
    print('Safe mode enabled.')
else:
    safe = False
if not mqtt:
    print('Exchange :', exchange)
    print('Currency : ', currency)
    print('Quantity:', quantity)


# Program Flow

if mqttd:
    mq.subscribe()
    while True:
        try:
            time.sleep(0.25)
        except KeyboardInterrupt:
            print('\nThank You For Moving Funds. Quitting!\n')
            sys.exit(0)


if get_address:
    #exchange = deposit_exchange
    print('Grabbing deposit address')
    timeStamp = tWrap.tS()
    logging.info("Get address request initated at %s" % timeStamp)
    ret = tWrap.deposit_address(deposit_exchange, currency)
    print(ret)
    sys.exit(0)

if withdraw:
    if currency == 'XRP' == 'XLM' == 'STR':
        print('Payment ID\'s are not yet supported. ')
        sys.exit(1)
    if deposit_exchange == 'poloniex' or 'bittrex' or 'cex' or 'binance':
        if exchange == 'bittrex' or 'poloniex' or 'binance':
            print(
                "Withdrawal requested : %s > %s" %
                (exchange, deposit_exchange))
            print("Getting adderess for %s ..." % deposit_exchange)
            _address = tWrap.deposit_address(deposit_exchange, currency)
            print(
                'Address for %s on %s is: %s' %
                (currency, deposit_exchange, _address))
            timeStamp = tWrap.tS()
            logging.info("Withdraw initatiated at %s " % timeStamp)
            logging.info(
                'Live: %s Withdraw from: %s Deposit into: %s Currency: %s Quantity: %s Address: %s' %
                (live, exchange, deposit_exchange, currency, quantity, _address))
            if safe:
                proceed = input(
                    'Live: %s Withdraw from: %s Deposit into: %s Currency: %s Quantity: %s Address: %s , procceed (YES/No): ' %
                    (live, exchange, deposit_exchange, currency, quantity, _address))
            else:
                proceed = 'YES'
            if proceed == 'YES' or not safe:
                ret = tWrap._withdraw(
                    live, exchange, currency, quantity, _address)

                print(ret)
                logging.info("Withdrawl function returned: " + str(ret))
            else:
                print('Withdrawal cancled at user request.')
                sys.exit(0)

        else:
            print(
                'Unsupport withdrawal exchange. Valid withdrawl exchanges are %s' %
                wdex)
            sys.exit(1)
    else:
        print('Invalid exchange. Valid destination exchanges are %s' % dpex)
        sys.exit(1)
