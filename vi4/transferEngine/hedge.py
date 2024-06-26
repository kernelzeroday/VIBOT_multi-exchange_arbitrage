#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Anon, Z & Devteam6, 2018
from sys import exit
import paho.mqtt.client as mqtt

import requests
import random
import json
from decimal import *


def getJSON(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error: %s", err)
    else:
        if "json" in r.headers.get('content-type', ""):
            try:
                res = r.json()
            except ValueError as err:
                print("ValueError: %s", err)
            else:
                return res
    return False


BTC_PRECISION = Decimal('0.00000001')

EXCHANGES = {}
VOLUME = Decimal()


def mqPublish(msg, topic='hedge'):
    client = mqtt.Client(client_id="hedgebot", clean_session=False)
    client = mqtt.Client('vihedger')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("localhost", 1883, 60)
    try:
        client.publish(topic, str(msg))
    except Exception as err:
        print(err)
    finally:
        client.disconnect()


class Exchange:
    def __init__(self, name, pairs={}, inversePairs={}, volumeTotal=Decimal()):
        global VOLUME
        global EXCHANGES
        self.name = name
        self.pairs = pairs
        self.inversePairs = inversePairs
        self.volumeTotal = volumeTotal
        VOLUME += volumeTotal

        if not self.pairs:
            raise ValueError("Pairs are requried")

        # Set Hedge Ratios
        remainder = Decimal(100)
        for pair in pairs.values():
            ratio = (
                pair.get("volume", Decimal())
                * Decimal(100) / self.volumeTotal
            ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            pair["hedgeRatio"] = ratio
            remainder -= ratio
        # Randomly assign the remainder
        if remainder:
            randKey = random.choice(list(self.pairs.keys()))
            self.pairs[randKey]["hedgeRatio"] += remainder
            print("%s: Assigned hedge remainder (%s%%) randomly to %s" % (
                self.name, remainder, randKey))

        EXCHANGES[self.name] = self


class Bittrex(Exchange):
    def __init__(self, name):
        pairs = {
            "BTC_XRP": {"name": "BTC-XRP"},
            "BTC_ETH": {"name": "BTC-ETH"},
            "BTC_DASH": {"name": "BTC-DASH"},
            "BTC_ZEC": {"name": "BTC-ZEC"},
            "BTC_XLM": {"name": "BTC-XLM"},
            "BTC_LTC": {"name": "BTC-LTC"},
            "BTC_LSK": {"name": "BTC-LSK"},
            "BTC_ETC": {"name": "BTC-ETC"},
            "BTC_XMR": {"name": "BTC-XMR"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

        # Get market volumes
        resp = getJSON(
            "https://bittrex.com/api/v1.1/public/getmarketsummaries")
        summary = resp.get("result", False)
        if summary:
            for entry in summary:
                pair = inversePairs.get(entry.get("MarketName", ""))
                if pair:
                    vol = Decimal(entry.get("BaseVolume", 0)).quantize(
                        BTC_PRECISION, rounding=ROUND_DOWN
                    )
                    pairs[pair]["volume"] = vol
                    volumeTotal += vol

        super().__init__(
            name,
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)


class Cex(Exchange):
    def __init__(self, name):
        pairs = {
            "BTC_XRP": {"name": "XRP/BTC"},
            "BTC_ETH": {"name": "ETH/BTC"},
            "BTC_DASH": {"name": "DASH/BTC"},
            "BTC_ZEC": {"name": "ZEC/BTC"},
            "BTC_XLM": {"name": "XLM/BTC"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

        # Get market volumes
        resp = getJSON("https://cex.io/api/tickers/BTC")
        tickers = resp.get("data", False)
        if tickers:
            for entry in tickers:
                pair = inversePairs.get(
                    entry.get("pair", "").replace(":", "/"), False)
                if pair:
                    quoteVol = Decimal(entry.get("volume", 0))
                    rate = Decimal(entry.get("last", 0))
                    vol = (quoteVol * rate).quantize(
                        BTC_PRECISION, rounding=ROUND_DOWN
                    )
                    pairs[pair]["volume"] = vol
                    volumeTotal += vol

        super().__init__(
            name,
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)


class Poloniex(Exchange):
    def __init__(self, name):
        pairs = {
            "BTC_XRP": {"name": "BTC_XRP"},
            "BTC_ETH": {"name": "BTC_ETH"},
            "BTC_DASH": {"name": "BTC_DASH"},
            "BTC_ZEC": {"name": "BTC_ZEC"},
            "BTC_XLM": {"name": "BTC_STR"},
            "BTC_LTC": {"name": "BTC_LTC"},
            "BTC_LSK": {"name": "BTC_LSK"},
            "BTC_ETC": {"name": "BTC_ETC"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

        # Get market volumes
        tickers = getJSON("https://poloniex.com/public?command=returnTicker")
        for k, v in pairs.items():
            vol = Decimal(tickers.get(
                v.get("name", False), {})
                .get("baseVolume", 0)
            ).quantize(
                BTC_PRECISION, rounding=ROUND_DOWN
            )
            pairs[k]["volume"] = vol
            volumeTotal += vol
        super().__init__(
            name,
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)


"""
def printHedge():
    global VOLUME
    global EXCHANGES
    for ExName, Ex in EXCHANGES.items():
        for PairName, Pair in Ex.pairs.items():
            print("%s\t- %s\t%s %%" % (ExName, PairName, Pair["hedgeRatio"]))
        print("%s\t- TOTAL BTC:\t%s (%s %%)" % (
            ExName, Ex.volumeTotal, (Ex.volumeTotal * Decimal('100') / VOLUME).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))
"""


def pubHedge():
    global VOLUME
    global EXCHANGES
    for ExName, Ex in EXCHANGES.items():
        for PairName, Pair in Ex.pairs.items():
            #print("%s\t- %s\t%s %%" % (ExName, PairName, Pair["hedgeRatio"]))
            message = (
                '{"exchange" : "%s", "pair" : "%s", "ratio" : "%s"}' %
                (ExName, PairName, Pair["hedgeRatio"]))
            mqPublish(message, 'hedge')
            print(message)
        print(
            "%s\t- TOTAL BTC:\t%s (%s %%)" %
            (ExName,
             Ex.volumeTotal,
             (Ex.volumeTotal *
              Decimal('100') /
              VOLUME).quantize(
                 Decimal('0.01'),
                 rounding=ROUND_DOWN)))


bit = Bittrex("BTRX")
cex = Cex("CEX")
pol = Poloniex("POLX")

# printHedge()
pubHedge()
