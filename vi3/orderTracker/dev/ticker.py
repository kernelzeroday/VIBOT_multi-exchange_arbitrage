#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# so, this is a work in progress, but the engine does work as it is now
# this will be more effecient reading from the websockets whenever i update it
# butits fine for now
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import config
import json
import sys
import pprint
debug = False


def mqConnect(client, userdata, flags, rc):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param flags:       Dict of broker reponse flags
    :param rc:          Int of connection state from 0-255:
                            0: Successful
                            1: Refused: Incorrect Protocol
                            2: Refused: Invalid Client ID
                            3: Refused: Server Unavailable
                            4: Refused: Incorrect User/Password
                            5: Refused: Not Authorised
    """
    if rc == 0:
        print("Connected Successfully")
    else:
        print("Refused %s" % rc)


def mqDisconnect(client, userdata, rc):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param rc:          Int of disconnection state:
                            0: Expected Disconnect IE: We called .disconnect()
                            _: Unexpected Disconnect
    """
    if rc == 0:
        print("Disconnected")
    else:
        print("Error: Unexpected Disconnection")


def mqPublish(msg, topic='ticker'):
    global CLIENTS
    client = mqtt.Client(client_id="ticker", clean_session=False)
    if not client:
        raise ValueError("Could not find an MQTT Client.")
    #client = mqtt.Client()
    client.username_pw_set(username=config.mq_user, password=config.mq_pass)
    # client.connect("localhost",1883,60)
    #publish.single(topic, str(msg));
    publish.single(
        topic,
        str(msg),
        hostname=config.mq_host,
        port=config.mq_port,
        auth={
            'username': config.mq_user,
            'password': config.mq_pass})
    # client.disconnect();


def mqParse(client, userdata, message):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param message:     Dict of message details: {
                            topic:      String of the message topic
                            payload:    Bytes of the message body
                            qos:        Int of QoS state:
                                            0: Sent once without confirmation
                                            1: Sent at least once with confirmation required
                                            2: Sent exactly once with 4-step handshake.
                            retain:     Bool of Retain state
                        }
    """
    #if debug: print(message.payload)
    #bittrex = ""
    #poloniex = ""
    #cex = ""
    try:
        obj = json.loads(message.payload)
    except Exception as err:
        print(err)

    try:
        bittrex = obj['bittrex']
    except Exception as err:
        print(err)
        pass
    else:

        exchange = 'bittrex'
        try:
            pair = bittrex['Pair']
        except BaseException:
            pass
        try:
            bidPrice = bittrex['MaxBid']['Price']
        except BaseException:
            pass
        try:
            askPrice = bittrex['MinAsk']['Price']
        except BaseException:
            pass
        try:
            t = str(
                '{"exchange":"%s","Market":\"%s\","Ask":"%s","Bid":"%s"}' %
                (exchange, pair, askPrice, bidPrice))
            #t = json.dumps({'exchange': exchange, 'Market': pair, 'Ask': askPrice, 'Bid': bidPrice},sort_keys=False)
            #t = json.loads(t)
        except Exception as err:
            # print(err)
            pass
        else:
            mqPublish(t)
            if debug:
                print(t)
            topic = str('ticker' + '/' + str(exchange) + '/' + str(pair))
            if debug:
                print(topic)
            mqPublish(t, topic)
            # return

    try:
        poloniex = obj['poloniex']
    except Exception as err:
        print(err)
        pass
    else:
        exchange = 'poloniex'
        try:
            pair = poloniex['Pair']
        except BaseException:
            pass
        try:
            bidPrice = poloniex['MaxBid']['Price']
        except BaseException:
            pass

        try:
            askPrice = poloniex['MinAsk']['Price']
        except BaseException:
            pass

        try:
            #t = json.dumps({'exchange': exchange, 'Market': pair, 'Ask': askPrice, 'Bid': bidPrice},sort_keys=False)
            #t = json.loads(t)
            t = str(
                '{"exchange":"%s","Market":\"%s\","Ask":"%s","Bid":"%s"}' %
                (exchange, pair, askPrice, bidPrice))
        except Exception as err:
            # print(err)
            pass
        else:
            mqPublish(t)
            if debug:
                print(t)
            topic = str('ticker' + '/' + str(exchange) + '/' + str(pair))
            if debug:
                print(topic)
            mqPublish(t, topic)
            # return

    try:
        cex = obj['cex']
    except Exception as err:
        # print(err)
        pass
    else:
        exchange = 'cex'
        try:
            pair = cex['Pair']
        except BaseException:
            pass
        try:
            bidPrice = cex['MaxBid']['Price']
        except BaseException:
            pass
        try:
            askPrice = cex['MinAsk']['Price']
        except BaseException:
            pass
        try:
            #t = json.dumps({'exchange': exchange, 'Market': pair, 'Ask': askPrice, 'Bid': bidPrice},sort_keys=False)
            #t = json.loads(t)
            t = str(
                '{"exchange":"%s","Market":\"%s\","Ask":"%s","Bid":"%s"}' %
                (exchange, pair, askPrice, bidPrice))
        except Exception as err:
            print(err)
        else:
            # mqPublish(t)
            if debug:
                print(t)
            topic = str('ticker' + '/' + str(exchange) + '/' + str(pair))
            if debug:
                print(topic)
            mqPublish(t, topic=topic)
            # return


def mqStart(streamId):
    """ Helper function to create a client, connect, and add to the Clients recordset
    :param streamID:    MQTT Client ID
    :returns mqtt client instance
    """
    global CLIENTS
    client = mqtt.Client(streamId, clean_session=False)
    client.username_pw_set(config.mq_user, config.mq_pass)
    # Event Handlers
    client.on_connect = mqConnect
    client.on_disconnect = mqDisconnect
    client.on_message = mqParse
    # Client.message_callback_add(sub, callback) TODO Do we want individual handlers?
    # Connect to Broker
    client.connect(
        config.mq_host,
        port=config.mq_port,
        keepalive=config.mq_keepalive,
        bind_address=config.mq_bindAddress)
    # Subscribe to Topics
    client.subscribe("/ticker/#")  # TODO Discuss QoS States
    client.loop_start()
    return client


mq_pubtop = 'ticker'
client = mqStart("tickerbot")

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
        sys.exit(0)
