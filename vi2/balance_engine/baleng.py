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
#from buysell import *

# hacky config

import tradeconf
mq_pubtop = 'bal'
debug = False
demo = False
# time
timeStamp = time.time()


def tStamp():
    t = time.time()
    t = str(t)
    return(t)


# logger stuff
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('balengine.log')
handler.setLevel(logging.INFO)
# create a logging format


import poloniex
import cexio
import json
import sys
""" (less) hacky config """

poloniexkey = str(tradeconf.poloniexkey)
poloniexsecret = str(tradeconf.poloniexsecret)
cexiousername = str(tradeconf.cexiousername)
cexiokey = str(tradeconf.cexiokey)
cexiosecret = str(tradeconf.cexiosecret)


""" init apis """
polo = poloniex.Poloniex(poloniexkey, poloniexsecret)
cex = cexio.Api(cexiousername, cexiokey, cexiosecret)


def polo_balance():
    try:
        bal = polo.returnAvailableAccountBalances('all')
    except Exception as whathefuckmylifegoddamnityoufuckers:
        logger.info(whathefuckmylifegoddamnityoufuckers)
        return False
    else:
        ret = json.dumps(bal)
        #logging.info("Balance call: "+ret)
        return(str(ret))


def cex_balance():
    try:
        #api = cexapi.API(conf.username, conf.api_key, conf.api_secret)
        api = cexio.Api(
            tradeconf.cexiousername,
            tradeconf.cexiokey,
            tradeconf.cexiosecret)
        try:
            cbal = json.dumps(api.balance)
        except Exception as err:
            print(err)
            return False
        else:
            # print(bal)
            #bal = json.dumps(bal)
            return(str(cbal))
    except Exception as err:
        print("Error: %s" % err)
        return False

# lets send a message


def mqsend(message, topic=mq_pubtop):
    """ Publishes a message to pubtop """
    _ts = tStamp()
    client = mqtt.Client()
    message_ = str(message)
    mq_pubtop_ = str(topic)
   # try:
   #     json.loads('{"timestamp" : "%s", "output" : "%s" }' % (_ts,message_))
   # except Exception as err:
   #     logger.info(err)
   #     return False
   # else:
   #msg=json.loads('{"timestamp" : "%s", "output" : "%s" }' % (_ts,message_))
    logger.info("Publishing message: %s to topic: %s" % (message_, mq_pubtop_))
    try:
        publish.single(
            mq_pubtop_,
            payload=str(message),
            hostname=mq_host,
            port=mq_port,
            auth={
                'username': mq_user,
                'password': mq_pass})
    except Exception as err:
        logger.info('ERROR publishing message: ' + err)
        pass

# lets log our messages to a file


def on_message(client, userdata, msg):
    """ do something with message  """
    try:
        obj = json.loads(msg.payload.decode('UTF-8'))
    except Exception as err:
        logger.info('ERROR: %s error loading json!' % err)
        pass
    #currs=['ETH', 'XRP', 'DASH', 'ZEC']


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

# def on_disconnect():


# wrap it all up nice with a bow on top

def mq_connect():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(mq_host, mq_port, 60)
    client.username_pw_set(username=mq_user, password=mq_pass)
    client.on_message = on_message
    client.loop_start()

    """ initialize mqtt subscription(s) """


# TODO: this should be a config file not hardcoded
mq_host = '172.31.21.170'
mq_port = 1883
mq_user = 'vibot'
mq_pass = 'NmQ5Nj_3MrAwiNDu'
mq_subtop = 'trade'
mq_pubtop = 'bal'
# mq_connect()


# you here? let me show you what i had in mind
# ah here
# ok


# so i was thinking, and this could be valid fo either method, something
# simple like this;

while True:
    try:
        cx_bal = cex_balance()
    except BaseException:
        pass
    try:
        pb_bal = polo_balance()
    except BaseException:
        pass
    if debug:
        print(cx_bal)
    if debug:
        print(pb_bal)
    try:
        mqsend(cx_bal, 'cbal')
    except Exception as FUCK:
        print(FUCK)
        logger.info(FUCK)
    try:
        mqsend(pb_bal, 'pbal')
    except Exception as fuck:
        print(fuck)
        logger.info(fuck)
    time.sleep(2)

# so than, this just keeps grabbing balance data and than we can do whateevere with it.
# thats great, we can run it on another box continuously and then we just make a filter in the order engine that grabs it and compares the current balance object to the trade object right
# ya i like that idea, that way dont have to muck around with the trade engine that currenly works great otherwise
# the only question is if we do it directly inside the order engine or if we make this a seperate filter that passes into the order engine, thats going to be your call
# ok when you say order engine you are refering to the trade engine right?
# data -> trade -> order aka mqbuysell
# ok ya, currently buysell (what i think of as the 'trade engine' reads from topic trade so we can do like , \
# umm, sec..
# psuedo code
# sub -t trade > something ; while read something ; do if [[ our logic ]] then pub -t orders , that make sense to you
#  yes exaaaaactly we can do it as a simple  filter between engines without any modifications to the internal logic or muching with python and such
# we can just slap a quick hack using jq or something and get it up and running, then do it in something faster like python tomorrow i just want it quick and dirty so they pay us
# ok, i dont think it would be very hard to do this in python, but ya, an
# sh poc could look like this..
