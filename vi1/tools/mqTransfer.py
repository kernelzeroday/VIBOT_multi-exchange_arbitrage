#!/usr/bin/env python3.6
# Author ~ DarkerEgo, 2017
# xelectron@protomail.com

""" MqTransfer - Program to manually craft transfer requests. Run --help for usage. Run with -i for interactive prompt mode. Run with -d for debug or dry_run mode. """

import sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import optparse
import sys
# mq_host='13.56.150.127'
mq_host = 'localhost'
mq_port = 1883
mq_user = 'vibot'
mq_pass = 'NmQ5Nj_3MrAwiNDu'
demo = True
mq_pubtop = ''


def reqTransfer(
        topic=mq_pubtop,
        mode='interative',
        fromex=None,
        toex=None,
        currency=None,
        quantity=0.0):
    """ function that crafts our json request """
    # set MqTT variables
    client = mqtt.Client(client_id="publish_test", clean_session=False)
    client = mqtt.Client('manual_tranfer')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect(mq_host, 1883, 60)
    # Prompt for parameters if interactive
    if mode == 'interactive':
        try:
            print('Notice: Interactive Mode >>')
            print('Manual Funds Mangement Client: ')
            currency_ = input('>> Currency: ')
            amount_ = input('>> Quanity: ')
            from_ = input('>> From Exchange: ')
            to_ = input('>> To Exchange: ')
        except KeyboardInterrupt:
            client.disconnect()
            sys.exit(0)
        else:
            msg = str(
                '{"action":"transfer","currency":"%s","amount":%s,"from":"%s","to":"%s"}' %
                (currency_, amount_, from_, to_))
            print('Message: ' + str(msg))
            verify = input('Send? y/n :')
            if verify != 'y':
                sys.exit(1)
            publish.single(
                mq_pubtop,
                payload=str(msg),
                hostname=mq_host,
                port=mq_port,
                auth={
                    'username': mq_user,
                    'password': mq_pass})
            return
    # Otherwise read parameters from the CLI
    elif mode == 'cli':
        if currency and quantity and fromex and toex:
            msg = str(
                '{"action":"transfer","currency":"%s","amount":%s,"from":"%s","to":"%s"}' %
                (currency, quantity, fromex, toex))
            print('Sending Request: ' + msg + '\n')
            publish.single(
                mq_pubtop,
                payload=str(msg),
                hostname=mq_host,
                port=mq_port,
                auth={
                    'username': mq_user,
                    'password': mq_pass})
        else:
            print('Missing arguments!')
            return False
    client.disconnect()


# Program start - parse and print args
print('[*] ARGV      :', sys.argv[1:])
parser = optparse.OptionParser()
parser.add_option('-i', '--interactive',
                  dest="interactive",
                  action="store_true",
                  default=False,
                  )

parser.add_option('-d', '--debug',
                  dest="debug",
                  default=False,
                  action="store_true",
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


parser.add_option('-f', '--from',
                  dest="from_exchange",
                  type="str",
                  )

parser.add_option('-t', '--to',
                  dest="to_exchange",
                  type="str",
                  )

options, remainder = parser.parse_args()

interactive = options.interactive
debug = options.debug
source = options.from_exchange
dest = options.to_exchange
currency = options.currency
quantity = options.quantity


# if debug mode, publish to a null topic
if debug:
    mq_pubtop = 'transfers/test'
    print('Demo/debug mode: publishing to `transfers/test`')
else:
    print('Warning: Live Mode Enabled! Publishing to `transfers/incoming`')
    mq_pubtop = 'transfers/incoming'


# if interactive mode, prompt for input interactively (or specify all
# parameters on the CLI)
if interactive:
    print('Interactive Mode Enabled')
    # get these variables interactively, call reqTransfer function
    reqTransfer(topic=mq_pubtop, mode='interactive')
else:
    try:
        # get these variables from parsed options
        reqTransfer(
            topic=mq_pubtop,
            mode='cli',
            fromex=source,
            toex=dest,
            currency=currency,
            quantity=quantity)
    except Exception as err:
        print('Error: ' + str(err))
        sys.exit(1)
