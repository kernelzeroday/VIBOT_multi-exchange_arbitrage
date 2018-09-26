#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simple MqTT Sub/Pub Example
# Anon 2017 ~ DevTeam

""" imports and logging """

import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import logging
import json
import sys
import poloniex
import cex as cexio
import signal


def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


mq_pubtop = 'messages'
debug = True
demo = True
balances = {
    "cex": {},
    "poloniex": {},
}
# time
timeStamp = time.time()


def tStamp():
    t = time.time()
    t = str(t)
    return(t)


# logger stuff
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('mqpy.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
logger.info("Program start at %.8f" % timeStamp)

# (less) hacky config
poloniexkey = 'JVU0RT3L-T21AQL4S-N8PC9122-20Q417WA'
poloniexsecret = 'd9cbef8ce3332d53227d39d50683acc61e6ea641b9c3ccafd72e266fc58dd887fc08edd2a60a52e3434d3ac00f1d40c2dc741a84f69529b13e012ce87532b450'
cexiousername = 'up109970818'
cexiokey = 'vHE9tsLrFFpb0uGz66ou6RwdZY'
cexiosecret = 'H3xmGc2T04pm4ftv5yqAO8wBv68'

# init apis
polo = poloniex.Poloniex(poloniexkey, poloniexsecret)
cex = cexio.Api(cexiousername, cexiokey, cexiosecret)


# Buy/Sell Funx
def sell_cex(pair, amount, price):
    try:
        ret = cex.sell_limit_order(amount, price, pair)
    except Exception as err:
        logger.info(err)
        return 0
    else:
        ret = json.dumps(ret)
        order_info = json.loads(ret)
        # if debug: print(ret)
        try:
            order_type = order_info['type']
            order_id = order_info['id']
            order_time = order_info['time']
            order_price = order_info['price']
            order_amount = order_info['amount']
            order_pending = order_info['pending']
            order_complete = order_info['complete']
        except Exception as err:
            loggin.info(err)
            return 0
        else:
            mqsend("Sucess. Order ID: %s posted at %s  " % (order_id, order_time,))
            logging.info("Sucess. Order ID: %s posted at %s  " % (order_id, order_time,))
            mqsend("Type: %s Amount: %s at %s Complete: %s Pending: %s" % (order_type, order_amount, order_price, order_complete, order_pending))
            logging.info("Type: %s Amount: %s at %s Complete: %s Pending: %s" % (order_type, order_amount, order_price, order_complete, order_pending))
            return order_id


def buy_cex(pair, amount, price):
    try:
        ret = cex.buy_limit_order(amount, price, pair)
    except Exception as err:
        logging.info(err)
        return 0
    else:
        ret = json.dumps(ret)
        order_info = json.loads(ret)
        # if debug: print(ret)
        try:
            order_type = order_info['type']
            order_id = order_info['id']
            order_time = order_info['time']
            order_price = order_info['price']
            order_amount = order_info['amount']
            order_pending = order_info['pending']
            order_complete = order_info['complete']
        except Exception as err:
            logger.info(err)
            return 0
        else:
            mqsend("Sucess. Order ID: %s posted at %s  " % (order_id, order_time))
            logging.info("Sucess. Order ID: %s posted at %s  " % (order_id, order_time))
            mqsend("Type: %s Amount: %s at %s Complete: %s Pending: %s" % (order_type, order_amount, order_price, order_complete, order_pending))
            logging.info("Type: %s Amount: %s at %s Complete: %s Pending: %s" % (order_type, order_amount, order_price, order_complete, order_pending))
            return order_id


def sell_polo(pair, price, amount):
    try:
        ret = polo.sell(pair, price, amount)
    except Exception as err:
        logger.info(err)
        return False
    else:
        ret_ = str(ret)
        logger.info("Sell polo order call: " + ret_)
        logger.info(ret_)
        mqsend(ret_)
        return True


def buy_polo(pair, price, amount):
    try:
        ret = polo.buy(pair, price, amount)
    except Exception as err:
        logging.info(err)
        return False
    else:
        ret_ = str(ret)
        logger.info("Buy polo order call: " + ret_)
        logger.info(ret_)
        mqsend(ret_)
        return True


# MqTT Functions
# lets send a message
def mqsend(message, topic=mq_pubtop):
    """ Publishes a message to pubtop """
    _ts = tStamp()
    client = mqtt.Client()
    message_ = str(message)
    mq_pubtop_ = str(topic)
    try:
        json.loads('{"timestamp" : "%s", "output" : "%s" }' % (_ts, message_))
    except Exception as err:
        logger.info(err)
        return False
    else:
        msg = json.loads('{"timestamp" : "%s", "output" : "%s" }' % (_ts, message_))
    logger.info("Publishing message: %s to topic: %s" % (msg, mq_pubtop_))
    try:
        publish.single(mq_pubtop_, payload=str(msg), hostname=mq_host, port=mq_port, auth = {'username': mq_user, 'password': mq_pass})
    except Exception as err:
        logger.info('ERROR publishing message: ' + err)
        pass


def on_message_pbal(client, userdata, msg):
    try:
        obj = json.loads(msg.payload.decode('UTF-8'))
    except Exception as err:
        logger.info("Error parsing balanace data %s" % err)
    else:
        # Standardise balances
        if "exchange" in obj:
            balances["poloniex"] = obj["exchange"]
            if debug:
                print("poloniex balance: %s" % balances["poloniex"])
                print(balances['poloniex']['BTC'])

def on_message_cbal(client, userdata, msg):
    try:
        obj = json.loads(msg.payload.decode('UTF-8'))
    except Exception as err:
        logger.info("Error parsing balanace data %s" % err)
    else:
        for key, val in obj.items():
            if "available" in val:
                balances["cex"][key] = val["available"]
        if debug:
            print("cex balance: %s" % balances["cex"])


# lets log our messages to a file
def on_message(client, userdata, msg):
    """ do something with message  """
    try:
        obj = json.loads(msg.payload.decode('UTF-8'))
    except Exception as err:
        logger.info('ERROR: %s error loading json!' % err)
        pass
    if debug:
        print(obj)

    try:
        buy_exchange = obj['buy']['exchange']
    except Exception as err:
        buy_exchange = 'null'
    try:
        sell_exchange = obj['sell']['exchange']
    except Exception as err:
        sell_exchange = 'null'

    try:
        buy_pair = obj['buy']['pair']
        sell_pair = obj['sell']['pair']
        buy_price = obj['buy']['price']
        sell_price = obj['sell']['price']
        buy_amount = obj['buy']['amount']
        sell_amount = obj['sell']['amount']
    except KeyError:
        pass
    try:
        buy_exchange_ = str(buy_exchange)
        sell_exchange_ = str(sell_exchange)
        buy_pair_ = str(buy_pair)
        sell_pair_ = str(sell_pair)
        buy_amount_ = str(buy_amount)
        sell_amount_ = str(sell_amount)
        buy_price_ = str(buy_price)
        sell_price_ = str(sell_price)
    except:
        pass
    else:
        try:
            logger.info("buy: exchange %s , pair %s , amt %s, price: %s / sell: exchange %s , pair %s , amt %s, price %s" % (buy_exchange_, buy_pair_, buy_amount_, buy_price_, sell_exchange_, sell_pair_, sell_amount_, sell_price_))
            # logger.info("buy exchange:  "+buy_exchange_+"  sell exchange:  "+sell_exchange_)
            # logger.info("buy pair:  "+buy_pair_+"  sell pair:  "+sell_pair_)
            # logger.info("buy amount:  "+buy_amount_+"  sell amount : "+sell_amount_)
            # logger.info("buy price: "+buy_price_+"  "+"  sell price : "+sell_price_)
        except Exception as err:
            logger.info(err)

    if sell_exchange_ is 'null' or buy_exchange_ is 'null':
        logger.info('No viable spread.')
        ts = tStamp()
        mqsend('No viable spread')
        pass

    if buy_exchange_ == 'poloniex':
        # bal = open("pbal.json", "r")
        # if float(buy_price_) > float(tradeconf.maxprice):
        #    mqsend("Buy price %s too high" % buy_price)
        #    pass
        if float(buy_amount_) < float(0.01):
            mqsend("Amount %s too low" % buy_amount_)
            do_trade = False
        else:
            do_trade = True
        # if float(sell_price_) < float(tradeconf.minprice):
        #    mqsend("Sell price %s too low" % (sell_price_))
        #    pass

        if not demo and do_trade:
            try:
                ret = buy_polo(buy_pair_, buy_price_, buy_amount_)
            except Exception as err:
                logger.debug('Error buying : ' + err)
                pass
            else:
                if not ret:
                    mqsend("ERROR: Error buying on polo!")
                    pass
                else:
                    logger.info('Successfully bought on polo!')
                    ret_ = str(ret)
                    mqsend("Successfully bought %s" % ret_)
                    try:
                        _ret = sell_cex(sell_pair_, sell_amount_, sell_price_)
                    except Exception as err:
                        logger.debug('Error selling: ' + str(err))
                        pass
                    else:
                        if not _ret:
                            ts = tStamp()
                            logger.info('ERROR: Error Selling on cex after buying on polo!')
                            mqsend('%s : ERROR: Error selling on cex after buying on polo!' % ts)
                        else:
                            ret__ = str(_ret)
                            logging.info("Success %s " % ret__)
                            mqsend("Successfully sold %s " % ret__)
        else:
            if do_trade:
                logger.debug('Amount too low to trade.')

            if demo:
                try:
                    print("Demo mode: buy %s %s %s" % (buy_pair_, buy_amount_, buy_price_))
                    mqsend("Demo mode: buy %s %s %s" % (buy_pair_, buy_amount_, buy_price_))
                    print("Demo mode: sell %s %s %s " % (sell_pair_, sell_amount_, sell_price_))
                    mqsend("Demo mode: sell %s %s %s " % (sell_pair_, sell_amount_, sell_price_))
                except:
                    pass

    if buy_exchange_ == 'cex':
        # if float(buy_price_) > float(tradeconf.maxprice):
        #    mqsend("Buy price %s too high" % buy_price)
        #    pass
        if float(buy_amount_) < float(0.01):
            mqsend("Amount %s too low" % buy_amount_)
            do_trade = False
        else:
            do_trade = True
        # if float(sell_price_) > float(tradeconf.minprice):
        #    mqsend("Sell price %s too low" % (sell_price_))
        #    pass

        if not demo and do_trade:
            try:
                ret__ = buy_cex(buy_pair, buy_amount_, buy_price_)
            except Exception as err:
                logger.debug('Error buying: ' + err)
                pass
            else:
                if not ret__:
                    mqsend("ERROR: Error buying on cex!")
                    pass
                else:
                    logger.info('Successfully bought on cex!')
                    ret___ = str(ret__)
                    mqsend("Successfully bought %s" % ret___)
                    try:
                        __ret = sell_polo(sell_pair_, sell_price_, sell_amount_)
                    except Exception as err:
                        logger.debug('Error selling: ' + err)
                        pass
                    else:
                        if not __ret:
                            ts = tStamp()
                            logger.info("ERROR: Error selling on polo after buying on cex!")
                            mqsend("%s :ERROR: Error selling on polo" % ts)
                        else:
                            logger.info('Successfully sold on polo')
                            mqsend(str(__ret))
        else:
            if do_trade:
                logger.debug('Amount too low to trade.')
            if demo:
                print("Demo mode: buy %s %s %s" % (buy_pair_, buy_amount_, buy_price_))
                mqsend("Demo mode: buy %s %s %s" % (buy_pair_, buy_amount_, buy_price_))
                print("Demo mode: sell %s %s %s " % (sell_pair_, sell_amount_, sell_price_))
                mqsend("Demo mode: sell %s %s %s " % (sell_pair_, sell_amount_, sell_price_))

    if buy_exchange_ == 'null':
        logger.debug('DEBUG: No viable spreads detected.')
    if buy_exchange_ == 'bittrex':
        logger.info('Unsupported buy exchange (bittrex support to be added in the future)')
        mqsend("Unsupported buy exchange: %s " % buy_exchange_)
    # logger.info(msg.topic+" "+str(obj))


# lets connect to the broker
def on_connect(client, userdata, flags, rc):
    """ Generic mqtt connect function """
    if rc == 0:
        mqsend("Connected to broker successfully. Result code: " + str(rc))
        logger.info("Mqtt connection succeeded with result code %s" % str(rc))
    else:
        mqsend("ERROR: Unable to connect to broker. Result code: " + str(rc))
        logger.info('ERROR: Unable to connect to broker: ' + str(rc))
        # sys.exit(1)
    # client.connect(mq_host)
    client.subscribe(mq_subtop)


def on_connect_pbal(client, userdata, flags, rc):
    """ Generic mqtt connect function """
    if rc == 0:
        mqsend("Connected to broker successfully. Result code: " + str(rc))
        logger.info("Mqtt connection succeeded with result code %s" % str(rc))
    else:
        mqsend("ERROR: Unable to connect to broker. Result code: " + str(rc))
        logger.info('ERROR: Unable to connect to broker: ' + str(rc))
        # sys.exit(1)
    # client.connect(mq_host)
    client.subscribe(mq_subtop_pbal)


def on_connect_cbal(client, userdata, flags, rc):
    """ Generic mqtt connect function """
    if rc == 0:
        mqsend("Connected to broker successfully. Result code: " + str(rc))
        logger.info("Mqtt connection succeeded with result code %s" % str(rc))
    else:
        mqsend("ERROR: Unable to connect to broker. Result code: " + str(rc))
        logger.info('ERROR: Unable to connect to broker: ' + str(rc))
        # sys.exit(1)
    # client.connect(mq_host)
    client.subscribe(mq_subtop_cbal)


# wrap it all up nice with a bow on top
def mq_connect():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(mq_host, mq_port, 60)
    client.username_pw_set(username=mq_user, password=mq_pass)
    client.on_message = on_message
    client.loop_start()


def mq_connect_pbal():
    client1 = mqtt.Client("pbal")
    client1.on_connect = on_connect_pbal
    client1.connect(mq_host, mq_port, 60)
    client1.username_pw_set(username=mq_user, password=mq_pass)
    client1.on_message = on_message_pbal
    client1.loop_start()


def mq_connect_cbal():
    client2 = mqtt.Client("cbal")
    client2.on_connect = on_connect_cbal
    client2.connect(mq_host, mq_port, 60)
    client2.username_pw_set(username=mq_user, password=mq_pass)
    client2.on_message = on_message_cbal
    client2.loop_start()


# initialize mqtt subscription(s)
# TODO: this should be a config file not hardcoded
mq_host = 'localhost'
mq_port = 1883
mq_user = 'vibot'
mq_pass = 'NmQ5Nj_3MrAwiNDu'
mq_subtop = 'trade'
mq_subtop_pbal = 'pbal'
mq_subtop_cbal = 'cbal'
mq_pubtop = 'messages'
mq_connect()
mq_connect_pbal()
mq_connect_cbal()

interactive = False
if not interactive:
    while 1:
        time.sleep(10)

