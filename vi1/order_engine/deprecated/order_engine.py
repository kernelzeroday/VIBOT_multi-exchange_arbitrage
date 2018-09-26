#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import *
import config
import time
import poloniex as PoloniexAPI
import cexio as CexAPI
import paho.mqtt.client as mqtt

Currencies = {}
Pairs = {}
Exchanges = {}
Balances = {}


class Currency:
    def __init__(self, name):
        self.name = name
        self.pairs = {}
        self.balances = {}
        Currencies[self.name] = self


class Pair:
    def __init__(self, currency, base, name=""):
        if isinstance(currency, Currency) and isinstance(currency, Currency):
            if not name:
                name = "_".join([base.name, currency.name])
            self.name = name
            self.currency = currency
            self.base = base
            Pairs[self.name] = self


class Balance:
    def __init__(self, currency, exchange):
        self.name = "_".join([currency.name, exchange.name])
        self.currency = currency
        self.exchange = exchange
        Balances[self.name] = self


class Exchange:
    def __init__(self, name="", pairs=[]):
        self.name = name
        self.pairs = {}
        self.balances = {}
        for pair in pairs:
            if pair in self.pairMap and pair in Pairs:
                p = Pairs[pair]
                self.pairs[pair] = p
                self.balances[p.currency] = Balance(p.currency, self)
                self.balances[p.base] = Balance(p.base, self)
        Exchanges[self.name] = self

    def checkBalance(self):
        return True

    def getBalance(self):
        return True

    def checkMin(self):
        return True

    def buy(self, currency, rate, qty):
        self.checkBalance()
        return True

    def sell(self, currency, rate, qty):
        self.checkBalance()
        return True


class Poloniex(Exchange):
    def __init__(self, pairs=[], key="", secret=""):
        self.pairMap = {
            "USD_BTC": "BTC:USD",
        }
        self.api = PoloniexAPI(config.poloniexKey, config.poloniexSecret)
        super().__init__("poloniex", pairs=pairs)
        self.getBalance()

    def getBalance(self):
        # Custom Logic
        return super().getBalance()

    def buy(self, currency, rate, qty):
        self.checkBalance()
        return True

    def sell(self, currency, rate, qty):
        self.checkBalance()
        return True


class Cex(Exchange):
    def __init__(self, pairs=[], key="", secret=""):
        self.pairMap = {
            "USD_BTC": "btcusd",
        }
        self.api = CexAPI(config.cexUser, config.cexKey, config.cexSecret)
        super().__init__("cex", pairs=pairs)
        self.getBalance()

    def getBalance(self):
        # Custom Logic
        return super().getBalance()

    def buy(self, currency, rate, qty):
        return super().buy(currency=currency, rate=rate, qty=qty)

    def sell(self, currency, rate, qty):
        return super().buy(currency=currency, rate=rate, qty=qty)




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
    print(message)


# MQTT Client Setup
Client = mqtt.Client("trade_stream", clean_session=False)
Client.username_pw_set(config.mq_user, config.mq_pass)
# Event Handlers
Client.on_connect = mqConnect
Client.on_disconnect =  mqDisconnect
Client.on_message = mqParse
# Client.message_callback_add(sub, callback) TODO Do we want individual handlers?
# Connect to Broker
Client.connect(config.mq_host, port=config.mq_port,
                    keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
# Subscribe to Topics
Client.subscribe([("trade", 0), ("pbal", 0), ("cbal", 0)])  # TODO Discuss QoS States
Client.loop_start()

while 1:
    time.sleep(0.25)

