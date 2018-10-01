#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Built in
import os
import sys
import signal
import time
import requests
import random
import json
from decimal import *
from collections import namedtuple
# 3rd Party
import okex from ccxt as OkexAPI
import poloniex as PoloniexAPI
import cexio as CexAPI
import bittrex as BittrexAPI
import paho.mqtt.client as mqtt
# Custom
import pairInfo
import config
net = float(135.0)

DEBUG = True
LIVE = True
ORDERBACK = True
INTERACTIVE = os.environ.get(
    'PYTHONINSPECT',
    False) or hasattr(
        sys,
        "ps1") or hasattr(
            sys,
    "ps2") or False
BTC_PRECISION = Decimal('0.00000001')
#PAIR_ARR = ["BTC_XRP", "BTC_ETH", "BTC_DASH", "BTC_ZEC", "BTC_XLM", "BTC_LTC", "BTC_ETC", "BTC_XMR", "BTC_LSK", "BTC_NEO", "ETH_OMG", "ETH_ETC", "ETH_GNT", "BTC_OMG"]
PAIR_ARR = pairInfo.PAIR_ARR
#SUBSCRIPTIONS = [("/spread"+v, 0) for v in PAIR_ARR]
# SUBSCRIPTIONS = [("/spread/#")]
SUBSCRIPTIONS = [("/spread/" + v, 0) for v in PAIR_ARR]
SUBSCRIPTIONS += [("pbal2", 0), ("cbal2", 0), ("bbal2", 0)]
LASTPROCESSED = {}

CURRENCIES = {}
PAIRS = {}
BALANCES = {}
EXCHANGES = {}
CLIENTS = {}
VOLUME = Decimal()


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


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


def pubprint(data):

    data_ = str("{'TRADE': " + str(data) + " }")
    try:
        mqPublish(id='trade', payload=data_, topic='messages')
    except Exception as err:
        pass
    print(data)


def debugPrint(msg):
    if DEBUG:
        print(msg)


class Currency:
    def __init__(self, name):
        global CURRENCIES
        self.name = name
        self.pairs = {}
        self.balances = {}
        CURRENCIES[self.name] = self

    def getTotal(self):
        available = pending = total = Decimal()
        for bal in self.balances.values():
            available += bal.available
            pending += bal.total - bal.available
            total += bal.total
        msg = (
            "Total: %s (%s Available, %s Pending)" %
            (total, available, pending))
        pubprint(msg)


class Pair:
    def __init__(self, name):
        """
        :param name:    Expects a pair name in the format <baseCurrency>_<quoteCurrency>
        """
        global PAIRS
        global CURRENCIES
        parts = name.split("_")
        if len(parts) != 2:
            raise ValueError(
                "Pair name must be in the format <baseCurrency>_<quoteCurrency>")
        self.name = name
        self.base = CURRENCIES.get(parts[0], False) or Currency(parts[0])
        self.quote = CURRENCIES.get(parts[1], False) or Currency(parts[1])
        self.exchanges = {}
        PAIRS[self.name] = self


class Balance:
    def __init__(self, exchange, currency=""):
        global BALANCES
        global CURRENCIES

        self.currency = CURRENCIES.get(currency, False)
        if not self.currency:
            raise ValueError("Invalid Currency %s" % currency)

        self.name = "_".join([currency, exchange.name])
        self.exchange = exchange
        self.available = Decimal(0)
        self.pending = Decimal(0)
        self.total = Decimal(0)
        self.Total = Decimal(0)
        self.reserved = Decimal(0)

        self.currency.balances[self.name] = self

        BALANCES[self.name] = self

    def update(self, available, pending):
        if self.available != available or self.pending != pending:
            self.available = available
            self.pending = pending
            self.total = available + pending
            self.Total_ = available + pending

            if not INTERACTIVE:
                pubprint(
                    "Updated %s %s Balance to: %s Available, %s Pending, %s Total" %
                    (self.exchange.name,
                     self.currency.name,
                     self.available,
                     self.pending,
                     self.total))
#                mqPublish('trade',msg_, topic='messages')

    def get(self):
        qty = self.available
        if self.reserved > 0:
            qty -= self.reserved
        if qty > 0:
            return qty
        else:
            return False


class Exchange:
    def __init__(
            self,
            name,
            pairs,
            inversePairs={},
            volumeTotal=Decimal(),
            fee=Decimal("0.0025")):
        global EXCHANGES
        global VOLUME
        global PAIRS

        if not pairs:
            raise ValueError("Pairs are requried")

        self.name = name
        self.pairs = pairs
        self.inversePairs = inversePairs
        self.fee = fee

        self.balances = {}
        for pairKey, pairVal in pairs.items():
            # Set up pairs
            p = PAIRS.get(pairKey, False)
            if not p:
                raise ValueError("Could not find pair %s" % pairKey)

            p.exchanges[self.name] = self
            # Set up balances
            quote = pairVal.get("quote", False)
            base = pairVal.get("base", False)
            if quote and not self.balances.get(quote, False):
                self.balances[quote] = Balance(self, currency=quote)
            if base and not self.balances.get(base, False):
                self.balances[base] = Balance(self, currency=base)

        # Set Hedge Ratios
        self.volumeTotal = volumeTotal
        if self.volumeTotal:
            VOLUME += volumeTotal
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
                pubprint(
                    "%s: Assigned hedge remainder (%s%%) randomly to %s" %
                    (self.name, remainder, randKey))

        EXCHANGES[self.name] = self

    def checkBalance(self, side, invPair, price, qty):
        SUGGEST = False
        """
        :param  side
        :param  invPairs
        :param  price
        :param  qty
        :return (balance, price, qty)
        """
        pair = self.pairs.get(self.inversePairs.get(invPair, False), False)
        if not pair:
            raise ValueError(
                "Could not find pair %s on %s" %
                (invPair, self.name))

        pairName = pair.get("name", False)
        if not pairName:
            raise ValueError(
                "Pair name not defined for %s on %s" %
                (invPair, self.name))

        qtyPrecision = pair.get("qtyPrecision")
        pricePrecision = pair.get("pricePrecision")
        if not (qtyPrecision and pricePrecision):
            raise ValueError(
                "Missing Qty Precision or Price Precision for %s %s" %
                (self.name, pairName))

        # Quantize Values
        qty = qty.quantize(qtyPrecision, rounding=ROUND_DOWN)
        price = price.quantize(pricePrecision, rounding=ROUND_DOWN)
        ratio = pair.get('hedgeRatio')
        #print('Hedge Ratio:' +str(ratio))
        # Check balance
        if side == "buy":
            currency = pair.get("base", False)
            # Make sure check is on the base currency BTC
            qty = (qty * price).quantize(BTC_PRECISION, rounding=ROUND_UP)
        elif side == "sell":
            currency = pair.get("quote", False)
        else:
            raise ValueError("No side defined")

        if not currency:
            raise ValueError("No currency found")

        balance = self.balances.get(currency, False)
        if not balance:
            raise ValueError(
                "Could not find balance for %s on %s" %
                (currency, self.name))

        available = balance.get()
        if available >= qty:
            pass
        elif available > 0:
            pubprint(
                "Qty changed for %s %s order due to lack of funds. From %s to %s" %
                (self.name, side, qty, available))
            qty = available
        else:
            if balance.total == 0.0 and SUGGEST:
                #sendAmt = float(balance.pending)  / 2
                exx = self.name
                exx = str(exx)
                currency = str(currency)
                msg_ = 'Suggest: Buy! Low Balance on ' + \
                    str(exx) + ' currency: ' + str(currency) + ' Target ratio :  ' + str(ratio)
                try:
                    mqPublish('trade', msg_, topic='messages')
                except Exception as err:
                    print('Error publishing: ' + str(err))
                    pass
            raise ValueError(
                "No %s available on %s (%s reserved, %s pending, %s total)" %
                (currency, self.name, balance.reserved, balance.pending, balance.total))
            ratio_ = str(ratio)
            # try:
            #    msg_ = str("""'{"action":"balance","amount":"%s", "currency":%s,"exchange":"%s"}'""" %(currency,ratio_,self.name))
            #    mqPublish('trade',msg_, topic='zenbot')
            # except Exception as err:
            #    print('Error publishing message'+str(err))
        if side == "buy":
            # Switch qty back
            qty = (qty / price).quantize(qtyPrecision, rounding=ROUND_DOWN)

        # Check minimum order qtys and values
        minType = pair.get("minType", False)
        if not minType:
            raise ValueError(
                "Could not find minType for %s %s" %
                (self.name, pairName))

        if minType == "qty":
            minQty = pair.get("minQty", False)
            if not minQty:
                raise ValueError(
                    "Could not find minQty for %s %s" %
                    (self.name, pairName))
            if qty < minQty:
                raise ValueError(
                    "Error: The requested %s order qty (%s) is too low for %s (%s)" %
                    (pairName, qty, self.name, minQty))

        elif minType == "val":
            minVal = pair.get("minVal", False)
            if not minVal:
                raise ValueError(
                    "Could not find minVal for %s %s" %
                    (self.name, pairName))
            val = (qty * price).quantize(pricePrecision, rounding=ROUND_DOWN)
            if val < minVal:
                raise ValueError(
                    "Error: The requested %s order value (%s) is too low for %s (%s)" %
                    (pairName, val, self.name, minVal))

        elif minType == "qtyval":
            minQty = pair.get("minQty", False)
            minVal = pair.get("minVal", False)
            if not (minQty and minVal):
                raise ValueError(
                    "Could not find minQty or minVal on %s %s" %
                    (self.name, pairName))
            if qty < minQty:
                raise ValueError(
                    "The requested %s order qty (%s) is too low for %s (%s)" %
                    (pairName, qty, self.name, minQty))
            val = (qty * price).quantize(pricePrecision, rounding=ROUND_DOWN)
            if val < minVal:
                raise ValueError(
                    "The requested %s order value (%s) is too low for %s (%s)" %
                    (pairName, val, self.name, minVal))
        else:
            raise ValueError(
                "Invalid minType for %s %s" %
                (self.name, pairName))

        return (balance, price, qty, ratio)

    def updateBalance(self, currency, available, pending):
        bal = self.balances.get(currency, False)
        if bal:
            bal.update(available, pending)

    def buy(
            self,
            pair,
            price,
            qty,
            kind="Arbitrage",
            orderID="",
            reference=""):
        # On completion publish message
        now = time.time()
        expires = 0
        later = random.randint(150, 300)
        if kind != "Arbitrage":
            expires = now + later
        msg = json.dumps({
            "Exchange": self.name,
            "Pair": pair,
            "Kind": kind,
            "Type": "buy",
            "OrderID": orderID,
            "Price": price,
            "Qty": qty,
            "Timestamp": now,
            "Expires": expires,
        }, cls=DecimalEncoder)
        try:
            mqPublish("trade", msg, topic="verified")
        except ValueError as err:
            print("MQTT Error: %s" % err)
        if DEBUG:
            print(msg)
        return True

    def sell(
            self,
            pair,
            price,
            qty,
            kind="Arbitrage",
            orderID="",
            reference=""):
        # On completion publish message
        now = time.time()
        expires = 0
        later = random.randint(150, 300)
        even_later = random.randint(300, 900)
        if kind == "Limit":
            expires = now + even_later
        elif kind == "Arbitrage":
            expires = now + later
        else:
            print('ERROR: Invalid Order Type' + str(kind))
        msg = json.dumps({
            "Exchange": self.name,
            "Pair": pair,
            "Kind": kind,
            "Type": "sell",
            "OrderID": orderID,
            "Price": price,
            "Qty": qty,
            "Timestamp": now,
            "Expires": expires,
        }, cls=DecimalEncoder)
        try:
            mqPublish("trade", msg, topic="verified")
        except ValueError as err:
            print("MQTT Error: %s" % err)
        if DEBUG:
            print(msg)
        return True


class Bittrex(Exchange):
    def __init__(self, pairs=[]):
        self.api = BittrexAPI.bittrex(config.bittrexKey, config.bittrexSecret)

        thisPairs = {}
        for p in pairs:
            pair = pairInfo.Bittrex.get(p, False)
            if pair:
                thisPairs[p] = pair
        pairs = thisPairs

        if not pairs:
            raise ValueError("Could not find any pairs")
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
            "bittrex",
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)

    def updateBalance(self, vals):
        # Parse vals
        try:
            res = json.loads(vals, parse_float=Decimal)
        except json.JSONDecodeError:
            # TODO Error decoding json
            pass
        else:
            for currency, data in res.items():
                if isinstance(data, dict):
                    available = data.get("available", Decimal())
                    pending = data.get("pending", Decimal())
                    super().updateBalance(currency, available, pending)

    def buy(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.buylimit(pair, str(qty), str(price))
            """
            :param pair:    string
            :param qty:     string
            :param price:   string
            :returns dict
                res = {
                    result: {"uuid" : ""},      <- we track this ID
                    message: "",
                }
            """
        except Exception as err:
            print("Bittrex Error Calling API.buylimit(): %s" % err)
            return False
        else:
            # ok so basically, is res defined anywhere else? let me show you
            # the eror i was getting before i did that.
            if not res.get("success", False):
                #               msg = res[res.index("message"), ""]
                msg = res.get("message", "")
                print("Bittrex Buy Order Placement Failed: %s" % msg)
                return False

            orderID = res.get("result", {}).get("uuid", False)
            if orderID:
                return super().buy(pair, price, qty, kind=kind, orderID=orderID)
            else:
                print(
                    "Bittrex Buy Order Warning: No orderID returned but API claims was successful!")

    def sell(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.selllimit(pair, str(qty), str(price))
            """
            :returns dict
                res = {
                    result: {"uuid" : ""},      <- we track this ID
                    message: "",
                }
            """
        except Exception as err:
            print("Bittrex Error Calling API.selllimit(): %s" % err)
            return False
        else:
            if not res.get("success", False):
                msg = res.get("message", "")
                print("Bittrex Sell Order Placement Failed: %s" % msg)
                return False

            orderID = res.get("result", {}).get("uuid", False)
            if orderID:
                return super().sell(pair, price, qty, kind=kind, orderID=orderID)
            else:
                print(
                    "Bittrex Sell Order Warning: No orderID returned but API claims was successful!")


class Okex(Exchange):
    def __init__(self, pairs=[]):
        self.api = OkexAPI
        self.api.apiKey = config.okexKey
        self.api.secret = config.okexSecret

        thisPairs = {}
        for p in pairs:
            pair = pairInfo.Okex.get(p, False)
            if pair:
                thisPairs[p] = pair
        pairs = thisPairs

        if not pairs:
            raise ValueError("Could not find any pairs")
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

# FIXME: verify this
        for pair in pairs:
            pair = inversePairs.get(entry.get("MarketName", ""))
            if pair:
                    vol = okex.fetch_ticker(pair)['info']['vol'].quantize(
                        BTC_PRECISION, rounding=ROUND_DOWN
                    )
                    pairs[pair]["volume"] = vol
                    volumeTotal += vol

        super().__init__(
            "okex",
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)

    def updateBalance(self, vals):
        # FIXME: format balances properly
        # Parse vals
        try:
            res = json.loads(vals, parse_float=Decimal)
        except json.JSONDecodeError:
            # TODO Error decoding json
            pass
        else:
            for currency, data in res.items():
                if isinstance(data, dict):
                    available = data.get("available", Decimal())
                    pending = data.get("pending", Decimal())
                    super().updateBalance(currency, available, pending)

    def buy(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.create_limit_buy_order(pair, str(qty), str(price))
            """
            :param pair:    string
            :param qty:     string
            :param price:   string
            :returns dict
                res = {
                    result: {"uuid" : ""},      <- we track this ID
                    message: "",
                }
            """
        except Exception as err:
            print("Okex Error Calling API.create_limit_buy_order(): %s" % err)
            return False
        else:
            # ok so basically, is res defined anywhere else? let me show you
            # the eror i was getting before i did that.
            if not res.get("success", False):
                #               msg = res[res.index("message"), ""]
                # FIXME: get the order id
                msg = res.get("message", "")
                print("Okex Buy Order Placement Failed: %s" % msg)
                return False

            orderID = res.get("result", {}).get("uuid", False)
            if orderID:
                return super().buy(pair, price, qty, kind=kind, orderID=orderID)
            else:
                print(
                    "Okex Buy Order Warning: No orderID returned but API claims was successful!")

    def sell(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.createLimitSellOrder(pair, str(qty), str(price))
            """
            :returns dict
                res = {
                    result: {"uuid" : ""},      <- we track this ID
                    message: "",
                }
            """
        except Exception as err:
            print("Okex Error Calling API.createLimitSellOrder(): %s" % err)
            return False
        else:
            if not res.get("success", False):
                # FIXME: get order id
                msg = res.get("message", "")
                print("Okex Sell Order Placement Failed: %s" % msg)
                return False

            orderID = res.get("result", {}).get("uuid", False)
            if orderID:
                return super().sell(pair, price, qty, kind=kind, orderID=orderID)
            else:
                print(
                    "Okex Sell Order Warning: No orderID returned but API claims was successful!")


class Cex(Exchange):
    def __init__(self, pairs=[]):
        self.api = CexAPI.Api(config.cexUser, config.cexKey, config.cexSecret)

        thisPairs = {}
        for p in pairs:
            pair = pairInfo.Cex.get(p, False)
            if pair:
                thisPairs[p] = pair
        pairs = thisPairs

        if not pairs:
            raise ValueError("Could not find any pairs")

        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()

        # Get market volumes
        resp = getJSON("https://cex.io/api/tickers/BTC")
        try:
            tickers = resp.get("data", False)
        except Exception as err:
            print('Error ' + str(err))
            sys.exit(1)
            #tickers = []
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
            "cex",
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal,
            fee=Decimal("0.0015"))

    def updateBalance(self, vals):
        # Parse vals
        try:
            res = json.loads(vals, parse_float=Decimal)
        except json.JSONDecodeError:
            # TODO Error decoding json
            pass
        else:
            for currency, data in res.items():
                if isinstance(data, dict):
                    available = data.get("available", Decimal())
                    pending = data.get("pending", Decimal())
                    super().updateBalance(currency, available, pending)

    def buy(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.buy_limit_order(str(qty), str(price), pair)
            """
            :param qty      string
            :param price    string
            :param pair     string
            :returns json (will require a json.loads())
            If limit order remains (Maker or Hybrid)
            {
                "complete": false,        bool
                "id": "89067468",         string      <- we track this ID
                "time": 1512054972480,    int
                "pending": "12.00000000", string
                "amount": "12.00000000",  string
                "type": "buy",            string="buy"
                "price": "1155.67"        string
            }
            If market order (Taker)
            {
                "symbol2Amount": "10000",     string
                "symbol1Amount": "19970000",  string
                "time": 1506615736816,        int
                "message": "...Bought 0.19970000 BTC for 100.00 USD",     string
                "type": "buy",                string="buy"
                "id": "88640269"              string      <- we track this ID
            }
            """
        except Exception as err:
            print("CEX Error Calling API.buy_limit_order(): %s" % err)
            return False
        else:
            orderID = res.get("id", False)
            if not orderID:
                print("CEX Buy Order Placement Failed")
                return False
            return super().buy(pair, price, qty, kind=kind, orderID=orderID)

    def sell(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.sell_limit_order(str(qty), str(price), pair)
            """
            As above with type:"sell".
            """
        except Exception as err:
            print("CEX Error Calling API.sell_limit_order(): %s" % err)
            return False
        else:
            orderID = res.get("id", False)
            if not orderID:
                print("CEX Sell Order Placement Failed")
                return False
            return super().sell(pair, price, qty, kind=kind, orderID=orderID)


class Poloniex(Exchange):
    def __init__(self, pairs=[]):
        self.api = PoloniexAPI.Poloniex(
            config.poloniexKey, config.poloniexSecret)
        self.currencyMap = {
            "STR": "XLM",
        }

        thisPairs = {}
        for p in pairs:
            pair = pairInfo.Poloniex.get(p, False)
            if pair:
                thisPairs[p] = pair
        pairs = thisPairs

        if not pairs:
            raise ValueError("Could not find any pairs")
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
            "poloniex",
            pairs=pairs,
            inversePairs=inversePairs,
            volumeTotal=volumeTotal)

    def updateBalance(self, vals):
        # Parse vals
        try:
            res = json.loads(vals, parse_float=Decimal)
        except json.JSONDecodeError:
            # TODO Error decoding json
            pass
        else:
            for currency, data in res.items():
                if isinstance(data, dict):
                    currency = self.currencyMap.get(
                        currency, currency)  # Map for STR -> XLM
                    available = data.get("available", Decimal())
                    pending = data.get("pending", Decimal())
                    super().updateBalance(currency, available, pending)

    def buy(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.buy(pair, str(price), str(qty))
            """
            :param pair:            string
            :param price:           string
            :param qty:             string
            :param orderType:       string - one of [False, 'fillOrKill', 'immediateOrCancel', 'postOnly']
            :returns dict
            {
                "orderNumber":31226040,     <- Track this ID
                "resultingTrades":[         <- Loop on trades... These will be market (taker) trades
                    {
                        "amount":"338.8732",
                        "date":"2014-10-18 23:03:21",
                        "rate":"0.00000173",
                        "total":"0.00058625",
                        "tradeID":"16164",  <- Trade IDs that fill this order
                        "type":"buy"
                    }
                ]
            }
            """
        except PoloniexAPI.PoloniexError as err:
            print("Poloniex Error Calling API.buy(): %s" % err)
            return False
        else:
            orderID = res.get("orderNumber", False)
            if not orderID:
                print("Poloniex Buy Order Placement Failed")
                return False
            # Pass relevant info for tracking and logging via this method's
            # super method (existing in the Exchange class)
            return super().buy(pair, price, qty, kind=kind, orderID=orderID)

    def sell(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.sell(pair, str(price), str(qty))
            """
            :returns dict
            As above with "type":"sell"
            """
        except PoloniexAPI.PoloniexError as err:
            print("Poloniex Error Calling API.sell(): %s" % err)
            return False
        else:
            orderID = res.get("orderNumber", False)
            if not orderID:
                print("Poloniex Sell Order Placement Failed")
                return False
            # Pass relevant info for tracking and logging via this method's
            # super method (existing in the Exchange class)
            return super().sell(pair, price, qty, kind=kind, orderID=orderID)


def percentage(percent, whole):
    if percent == 0.0:
        return float(0.0)
    else:
        try:
            return (percent * whole) / 100.0
        except BaseException:
            return(0.0)


def parseSpreads(pair, spreads):
    """ Trade Stream Parsing
    This is the centerpiece of this script
    """
    global ORDERBACK
    global EXCHANGES
    #BUYBACK = SELLBACK = False
    #ALLOW_BUYBACK = ALLOW_SELLBACK = True
    Spread = namedtuple('Spread',
                        ['Name',
                         'BuyFrom',
                         'BuyPrice',
                         'BuyQty',
                         'BuyFee',
                         'SellTo',
                         'SellPrice',
                         'SellQty',
                         'SellFee',
                         'Value',
                         'EMA',
                         'EMVAR',
                         'Score',
                         'EMAMaxPos',
                         'EMAAge',
                         'TimeStart',
                         'LastUpdate',
                         'Type',
                         'Count',
                         'EMARate',
                         'TimeLast'])
    try:
        spreads = json.loads(
            spreads,
            object_hook=lambda x: Spread(
                **x),
            parse_int=Decimal,
            parse_float=Decimal)
    except json.JSONDecodeError:
        print("JSON decode error")
        return
    else:
        for spread in spreads:
            check = LASTPROCESSED.get(spread.Name, Decimal())
            if spread.Type == 'steady' or spread.Count > 1:
                ORDERBACK = False
            else:
                ORDERBACK = True
            #print(spread, check)
            if spread.LastUpdate <= check:
                #print("Already Processed")
                continue
            buyEx = EXCHANGES.get(spread.BuyFrom, False)
            sellEx = EXCHANGES.get(spread.SellTo, False)

            if not (buyEx and sellEx):
                print("Couldn't find exchanges %s or %s" % (buyEx, sellEx))
                LASTPROCESSED[spread.Name] = Decimal(
                    (time.time() + 0.1) * 1000000000)
                continue
            buyPair = buyEx.pairs.get(pair, {}).get("name", False)
            sellPair = sellEx.pairs.get(pair, {}).get("name", False)
            if not (buyPair and sellPair):
                print(
                    "Couldn't find %s inverse pairs %s or %s" %
                    (pair, buyPair, sellPair))
                LASTPROCESSED[spread.Name] = Decimal(
                    (time.time() + 0.1) * 1000000000)
                continue
            try:
                buyBal, buyPrice, buyQty, ratio = buyEx.checkBalance(
                    "buy", buyPair, spread.BuyPrice, spread.BuyQty)
                sellBal, sellPrice, sellQty, ratio = sellEx.checkBalance(
                    "sell", sellPair, spread.SellPrice, spread.SellQty)
                # Cross Check
                if sellQty < buyQty:
                    buyBal, buyPrice, buyQty, ratio = buyEx.checkBalance(
                        "buy", buyPair, buyPrice, sellQty)
                elif buyQty < sellQty:
                    sellBal, sellPrice, sellQty, ratio = sellEx.checkBalance(
                        "sell", sellPair, sellPrice, buyQty)
            except ValueError as err:
                pubprint("Error computing balances: %s\n" % err)
            else:
                # Remember that this function is called in threads.
                # Reserve this qty for the following trades
                buyRes = buyBal.Total_
                sellRes = sellBal.Total_
                buyBal.reserved += buyQty
                sellBal.reserved += sellQty

                # Place the orders
                """ Arb Trades (Should be market orders, ie Taker Fees)
                With Instant Market Rebalance (Should be limit orders, ie Maker Fees)"""
                BUYBACK = SELLBACK = False
                if LIVE:
                    # Arb Sell
                    if sellEx.sell(sellPair, sellPrice, sellQty):
                        try:
                            pubprint('SellEx Ratio : ' + str(ratio))
                        except BaseException:
                            pass
                        try:
                            bAmt = float(net) / float(buyRes)
                            cRatio = percentage(bAmt, net)
                        except Exception as err:
                            pass
                        else:
                            if cRatio < ratio:
                                pubprint(
                                    'Allow Buyback:  Ratio: ' +
                                    str(cRatio) +
                                    ' Allocated Ratio: ' +
                                    str(ratio))
                                BUYBACK = True

                            # Arb buy
                            if buyEx.buy(buyPair, buyPrice, buyQty):
                                try:
                                    pubprint('BuyEx Ratio : ' + str(ratio))
                                except BaseException:
                                    pass
                                try:
                                    sAmt = float(net) / float(sellRes)
                                    cRatio = percentage(sAmt, net)
                                except Exception as err:
                                    pass
                                else:
                                    if cRatio > ratio:
                                        pubprint(
                                            'Allow SellBack: Ratio ' +
                                            str(cRatio) +
                                            ' Allocated Ratio: ' +
                                            str(ratio))
                                        SELLBACK = True

                else:
                    debugPrint(
                        "%s Sold %s %s at %s" %
                        (sellEx.name, sellQty, sellPair, sellPrice))
                    debugPrint(
                        "%s Bought %s %s at %s" %
                        (buyEx.name, buyQty, buyPair, buyPrice))
                    BUYBACK = SELLBACK = True

                if ORDERBACK and (BUYBACK or SELLBACK):

                    buyBackPrice = (buyPrice * (Decimal('1') - sellEx.fee))
                    buyBackQty = (buyQty * (Decimal('1') - sellEx.fee))
                    sellBackPrice = (sellPrice * (Decimal('1') + buyEx.fee))
                    sellBackQty = (sellQty * (Decimal('1') - buyEx.fee))

                    try:
                        sellBackBal, sellBackPrice, sellBackQty, ratio = buyEx.checkBalance(
                            "sell", buyPair, sellBackPrice, sellBackQty)
                        buyBackBal, buyBackPrice, buyBackQty, ratio = sellEx.checkBalance(
                            "buy", sellPair, buyBackPrice, buyBackQty)
                        # Cross Check
                        if buyBackQty < sellBackQty:
                            sellBackBal, sellBackPrice, sellBackQty, ratio = buyEx.checkBalance(
                                "sell", buyPair, sellBackPrice, buyBackQty)
                        elif sellBackQty < buyBackQty:
                            buyBackBal, buyBackPrice, buyBackQty, ratio = sellEx.checkBalance(
                                "buy", sellPair, buyBackPrice, sellBackQty)

                    except ValueError as err:
                        print("Error computing orderback balances: %s\n" % err)
                    else:
                        if BUYBACK:
                            buyBackBal.reserved += buyBackQty
                            if LIVE and BUYBACK:
                                sellEx.buy(
                                    sellPair, buyBackPrice, buyBackQty, kind="Limit")
                                buyBackBal.available -= buyBackQty
                                buyBackBal.reserved -= buyBackQty
                            else:
                                debugPrint(
                                    "%s Buy Order Placed for %s %s at %s" %
                                    (sellEx.name, buyBackQty, sellPair, buyBackPrice))

                        if SELLBACK:
                            sellBackBal.reserved += sellBackQty
                            if LIVE and SELLBACK:
                                buyEx.sell(
                                    buyPair, sellBackPrice, sellBackQty, kind="Limit")
                                sellBackBal.available -= sellBackQty
                                sellBackBal.reserved -= sellBackQty
                            else:
                                debugPrint(
                                    "%s Sell Order Placed for %s %s at %s" %
                                    (buyEx.name, sellBackQty, buyPair, sellBackPrice))

                """ Release balance reservation
                Reduce available quantity.
                This will then self correct via the balance streams.
                """
                buyBal.available -= buyQty
                sellBal.available -= sellQty
                buyBal.reserved -= buyQty
                sellBal.reserved -= sellQty
            LASTPROCESSED[spread.Name] = Decimal(
                (time.time() + 0.1) * 1000000000)
    return


# MQTT FUNCTIONS
def getTopicFunc(topic):
    """ This function maps incoming mq topics to a parsing function
    :param topic:   MQTT Subscription Topic
    :return         function to handle MQTT message body, or False
    """
    global EXCHANGES
    funcMap = {
        "bbal2": EXCHANGES["bittrex"].updateBalance if "bittrex" in EXCHANGES else False,
        "cbal2": EXCHANGES["cex"].updateBalance if "cex" in EXCHANGES else False,
        "pbal2": EXCHANGES["poloniex"].updateBalance if "poloniex" in EXCHANGES else False,
    }
    return funcMap.get(topic, False)


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
    if "/spread" in message.topic:
        pair = message.topic.replace("/spread/", "")
        parseSpreads(pair, message.payload)
    elif "SPREAD" in message.topic:
        pair = message.topic.replace("_SPREAD", "")
        parseSpreads(pair, message.payload)
    elif "bbal2" in message.topic:
        func = getTopicFunc(message.topic)
        if func:
            func(message.payload)
    elif "cbal2" in message.topic:
        func = getTopicFunc(message.topic)
        if func:
            func(message.payload)
    elif "pbal2" in message.topic:
        func = getTopicFunc(message.topic)
        if func:
            func(message.payload)
    else:
        func = getTopicFunc(message.topic)
        if func:
            func(message.payload)


def mqPublish(id, payload, topic=config.mq_pubtop, qos=0, retain=False):
    """ MQTT Publish Message to a Topic
    :param id           String of the Client ID
    :param topic:       String of the message topic
    :param payload:     String of the message body
    :param qos:         Int of QoS state:
                            0: Sent once without confirmation
                            1: Sent at least once with confirmation required
                            2: Sent exactly once with 4-step handshake.
    :param retain:      Bool of Retain state
    :return             Tuple (result, mid)
                            result: MQTT_ERR_SUCCESS or MQTT_ERR_NO_CONN
                            mid:    Message ID for Publish Request
    """
    global CLIENTS
    client = CLIENTS.get(id, False)
    if not client:
        raise ValueError("Could not find an MQTT Client matching %s" % id)
    client.publish(topic, payload=payload, qos=qos, retain=retain)
    if topic != 'messages':
        client.publish('messages', payload=payload, qos=qos, retain=retain)

    # print(str(payload))


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
    client.subscribe(SUBSCRIPTIONS)  # TODO Discuss QoS States
    client.loop_start()
    CLIENTS[streamId] = client
    return client


def printHedge():
    global VOLUME
    global EXCHANGES
    for ExName, Ex in EXCHANGES.items():
        for PairName, Pair in Ex.pairs.items():
            pubprint(
                "%s\t- %s\t%s %%" %
                (ExName, PairName, Pair["hedgeRatio"]))
            #hedgeRatio = PairName+ "_"
            # hedgeRatio.replace('_',Pair[hedgeRatio])
            # print(hedgeRatio)
        pubprint(
            "%s\t- TOTAL BTC:\t%s (%s %%)" %
            (ExName,
             Ex.volumeTotal,
             (Ex.volumeTotal *
              Decimal('100') /
              VOLUME).quantize(
                 Decimal('0.01'),
                 rounding=ROUND_DOWN)))


# MAIN
def main():
    global CLIENTS
    global PAIRS
    client = mqStart("trade")
    # Signal handling

    def signalHandler(signal, frame):
        try:
            (c.disconnect() for c in CLIENTS.values())
        except Exception as err:
            print(str(err))
            pass
        print("\nProgram exiting gracefully")
        sys.exit(0)
    signal.signal(signal.SIGINT, signalHandler)

    # Set up Pairs
    for pair in PAIR_ARR:
        Pair(pair)

    # Set up Exchanges
    Bittrex(PAIR_ARR)
    Cex(PAIR_ARR)
    Poloniex(PAIR_ARR)
    Okex(PAIR_ARB)

    printHedge()

    # Start a MQ Client
    #client = mqStart("trade")

    if not INTERACTIVE:
        # Infinite Loop if interactive
        while 1:
            time.sleep(0.25)


main()
