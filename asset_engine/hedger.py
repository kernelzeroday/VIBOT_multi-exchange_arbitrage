#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from sys import exit
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import requests,time
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


def mqPublish(msg,topic='messages'):
    client = mqtt.Client(client_id="hedgebot", clean_session=False)
    client = mqtt.Client('vihedger')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("localhost",1883,60)
    mq_pass = 'NmQ5Nj_3MrAwiNDu'
    mq_user = 'vibot'
    mq_port=1883
    try:
        #client.publish(topic, str(msg));
        publish.single(topic, payload=str(msg), hostname=mq_host, port=mq_port, auth = {'username': mq_user, 'password': mq_pass})
    except Exception as err:
        print(err)
    finally:
        client.disconnect();




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
            "BTC_XRP":  {"name": "BTC-XRP"},
            "BTC_ETH":  {"name": "BTC-ETH"},
            "BTC_DASH": {"name": "BTC-DASH"},
            "BTC_ZEC":  {"name": "BTC-ZEC"},
            "BTC_XLM":  {"name": "BTC-XLM"},
            "BTC_LTC":  {"name": "BTC-LTC"},
            "BTC_XMR":  {"name": "BTC-XMR"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

        # Get market volumes
        resp = getJSON("https://bittrex.com/api/v1.1/public/getmarketsummaries")
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

        super().__init__(name, pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)


class Cex(Exchange):
    def __init__(self, name):
        pairs = {
            "BTC_XRP":  {"name": "XRP/BTC"},
            "BTC_ETH":  {"name": "ETH/BTC"},
            "BTC_DASH": {"name": "DASH/BTC"},
            "BTC_ZEC":  {"name": "ZEC/BTC"},
            "BTC_XLM":  {"name": "XLM/BTC"},
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

        super().__init__(name, pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)


class Poloniex(Exchange):
    def __init__(self, name):
        pairs = {
            "BTC_XRP":  {"name": "BTC_XRP"},
            "BTC_ETH":  {"name": "BTC_ETH"},
            "BTC_DASH": {"name": "BTC_DASH"},
            "BTC_ZEC":  {"name": "BTC_ZEC"},
            "BTC_XLM":  {"name": "BTC_STR"},
            "BTC_LTC":  {"name": "BTC_LTC"},
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
        super().__init__(name, pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)


class Binance(Exchange):
    def __init__(self, name):
        pairs = {   # todo: where get required pairs?
            "BTC_XRP":  {"name": "XRPBTC"},
            "BTC_ETH":  {"name": "ETHBTC"},
            "BTC_DASH": {"name": "DASHBTC"},
            "BTC_ZEC":  {"name": "ZECBTC"},
            "BTC_XLM":  {"name": "XLMBTC"},
            "BTC_LTC":  {"name": "LTCBTC"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()
        tickers = getJSON('https://api.binance.com/api/v1/ticker/24hr')
        if not tickers:
            #todo: add log here
            return
        prep_tickers = self._tickers_to_dict(tickers)
        # Get market volumes
        for k, v in pairs.items():
            vol = Decimal(prep_tickers.get(
                self._pair_symbol_to_ex_style(v.get("name", False)), {})
                .get("volume", 0)      # "quoteVolume" is what we need??
            ).quantize(
                BTC_PRECISION, rounding=ROUND_DOWN
            )
            pairs[k]["volume"] = vol
            volumeTotal += vol
        super().__init__(name, pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)

    def _tickers_to_dict(self, tickers):
        result = {}
        for ticker in tickers:
            result[ticker['symbol']] = ticker
        return result

    def _pair_symbol_to_ex_style(self, pair):
        b_curr = pair[3:];q_curr = pair[:3]
        return "".join([q_curr,b_curr])


class Okex(Exchange):
    def __init__(self, name):
        pairs = {   # todo: where get pairs?
            "BTC_XRP":  {"name": "XRP/BTC"},
            "BTC_ETH":  {"name": "ETH/BTC"},
            "BTC_DASH": {"name": "DASH/BTC"},
            "BTC_ZEC":  {"name": "ZEC/BTC"},
            "BTC_XLM":  {"name": "XLM/BTC"},
            "BTC_LTC":  {"name": "LTC/BTC"},
        }
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()
        # Get market volumes
        for k, v in pairs.items():
            ticker = getJSON('https://www.okex.com/api/v1/ticker.do?symbol=%s' % self._pair_symbol_to_ex_style(k.lower()))  # todo: sync request for each pair, ask Chev if this permissible
            ticker = ticker['ticker']
            if self._check_ticker(ticker) is False:
                continue
            vol = Decimal(ticker.get("vol", 0)
            ).quantize(
                BTC_PRECISION, rounding=ROUND_DOWN
            )
            pairs[k]["volume"] = vol
            volumeTotal += vol
        super().__init__(name, pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)

    def _tickers_to_dict(self, tickers: list):
        result = {}
        for ticker in tickers:
            result[ticker['symbol']] = ticker
        return result

    def _check_ticker(self, ticker):
        expected_keys = ['high', 'vol', 'last', 'low', 'buy', 'sell']
        if not sorted(ticker.keys()) == sorted(expected_keys):
            #todo: add error log here
            return False
        return True

    def _pair_symbol_to_ex_style(self, pair):
        b_curr, q_curr = pair.split('_')
        return "_".join([q_curr.lower(),b_curr.lower()])



"""def printHedge():
    global VOLUME
    global EXCHANGES
    for ExName, Ex in EXCHANGES.items():
        for PairName, Pair in Ex.pairs.items():
            print("%s\t- %s\t%s %%" % (ExName, PairName, Pair["hedgeRatio"]))
        print("%s\t- TOTAL BTC:\t%s (%s %%)" % (
            ExName, Ex.volumeTotal, (Ex.volumeTotal * Decimal('100') / VOLUME).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))"""

def pubHedge():
    global VOLUME
    global EXCHANGES
    for ExName, Ex in EXCHANGES.items():
        for PairName, Pair in Ex.pairs.items():
            #print("%s\t- %s\t%s %%" % (ExName, PairName, Pair["hedgeRatio"]))
            message=('{"exchange" : "%s", "pair" : "%s", "ratio" : "%s"}' % (ExName, PairName, Pair["hedgeRatio"]))
            #pair_ = PairName
            #pair_ = PairName.split('_')
            #pair_ = pair_[1]
            #r = str(Pair["hedgeRatio"])
            #if pair == pair_:
            #    return('{' + pair_ + ":" + r+'}')
            mqPublish(message,'hedge')
            print(message)
        print("%s\t- TOTAL BTC:\t%s (%s %%)" % (
            ExName, Ex.volumeTotal, (Ex.volumeTotal * Decimal('100') / VOLUME).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))



bit = Bittrex("bittrex")
cex = Cex("cex")
pol = Poloniex("poloniex")
bin = Binance("binance")
oke = Okex("okex")

mq_host = 'localhost'
mq_port = 1883
mq_user = 'vibot'
mq_pass = 'NmQ5Nj_3MrAwiNDu'
mq_pubtop = 'messages'


#printHedge()
while 1:

    pubHedge()
    time.sleep(300)
#ret = getHedge('BTC_LTC')
#print(ret)
