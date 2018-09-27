#!/usr/bin/env python3.6
import json
import ccxt
import math
import config
tickers = []
bals = []
pairs = ['XRP/BTC','ETH/BTC','DASH/BTC',"XLM/BTC","ZEC/BTC","XMR/BTC"]
exchanges = ['bittrex','binance','cex','okex','poloniex']
currencies = ['XRP','ETH','DASH','ZEC','XLM','XMR']
def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

global cex
global poloniex
global binance
global bitrrex
global okex


binanceAPI = ccxt.binance({"apiKey":config.binanceKey, "secret":config.binanceSecret})
bittrexAPI = ccxt.bittrex({"apiKey":config.bittrexKey, "secret":config.bittrexSecret})
cexAPI = ccxt.cex({"apiKey":config.cexKey,"secret":config.cexSecret,"uid":config.cexUser})
okexAPI = ccxt.okex({"apiKey":config.okexKey,"secret":config.okexSecret})
poloniexAPI = ccxt.poloniex({"apiKey":config.poloniexKey,"secret":config.poloniexSecret})
okexAPI = ccxt.okex({"apiKey":config.okexKey,"secret":config.okexSecret})

binanceBals = {}
bittrexBals = {}
cexBals = {}
okexBals = {}
poloniexBals = {}

binanceTickers = {}
bittrexTickers = {}
cexTickers = {}
okexTickers = {}
poloniexTickers = {}

binanceBals = binanceAPI.fetch_total_balance()
bals += [(binanceBals)]
bittrexBals = bittrexAPI.fetch_total_balance()
bals += [(bittrexBals)]
cexBals = cexAPI.fetch_total_balance()
bals += [(cexBals)]
okexBals = okexAPI.fetch_total_balance()
bals += [(okexBals)]
poloniexBals = poloniexAPI.fetch_total_balance()
bals += [(poloniexBals)]

binanceTickers = binanceAPI.fetch_tickers(symbols=pairs)
tickers += ([binanceTickers])
bittrexTickers = bittrexAPI.fetch_tickers(symbols=pairs)
tickers += ([bittrexTickers])
cexTickers = cexAPI.fetch_tickers(symbols=pairs)
tickers += ([cexTickers])
okexTickers = okexAPI.fetch_tickers(symbols=pairs)
tickers += ([okexTickers])
poloniexTickers = poloniexAPI.fetch_tickers(symbols=pairs)
tickers += ([poloniexTickers])


print('Markets:')
for market in pairs:
    print(market)


for key, val in binanceTickers.items():
    if key in "ETH/BTC":
        binanceETH = val['ask']
    if key in 'XRP/BTC':
        binanceXRP = val['ask']
    if key in 'DASH/BTC':
        binanceDASH = val['ask']
    if key in 'ZEC/BTC':
        binanceZEC = val['ask']
    if key in 'XLM/BTC':
        binanceXLM = val['ask']
    if key in 'XMR/BTC':
        binanceXMR = val['ask']
        
for key, val in bittrexTickers.items():
    if key in "ETH/BTC":
        bittrexETH = val['ask']
    if key in 'XRP/BTC':
        bittrexXRP = val['ask']
    if key in 'DASH/BTC':
        bittrexDASH = val['ask']
    if key in 'ZEC/BTC':
        bittrexZEC = val['ask']
    if key in 'XLM/BTC':
        bittrexXLM = val['ask']
    if key in 'XMR/BTC':
        bittrexXMR = val['ask']


for key,val in cexTickers.items():
    
    if key in "ETH/BTC":
       cexETH = val['ask']
    if key in 'XRP/BTC':
        cexXRP = val['ask']
    if key in 'DASH/BTC':
        cexDASH = val['ask']
    if key in 'ZEC/BTC':
        cexZEC = val['ask']
    if key in 'XLM/BTC':
        cexXLM = val['ask']
    #if key in 'XMR/BTC':
    cexXMR = float('0')

for key,val in okexTickers.items():
    
    if key in "ETH/BTC":
       okexETH = val['ask']
    if key in 'XRP/BTC':
        okexXRP = val['ask']
    if key in 'DASH/BTC':
        okexDASH = val['ask']
    if key in 'ZEC/BTC':
        okexZEC = val['ask']
    if key in 'XLM/BTC':
        okexXLM = val['ask']
    if key in 'XMR/BTC':
        okexXMR = val['ask']



for key,val in poloniexTickers.items():
    if key in "ETH/BTC":
       poloniexETH = val['ask']
    if key in 'XRP/BTC':
        poloniexXRP = val['ask']
    if key in 'DASH/BTC':
        poloniexDASH = val['ask']
    if key in 'ZEC/BTC':
        poloniexZEC = val['ask']
    if key in 'XLM/BTC':
        poloniexXLM = val['ask']
    if key in 'XMR/BTC':
        poloniexXMR = val['ask']

# For future use
marketNames = []
for markets in pairs:
    market = market.split('/')
    market = market[0]

    for ex in exchanges:

        marketName = str(ex)+str(market)
        marketNames += [(marketName)]

#print(marketNames)



""" TODO: Fix this so it's a loop and not a run on if statement...

def calcSpreads(curr):
    if curr in currencies:
        cexSpread = str('cex')+str(curr)
        bittrexSpread = str('bittrex')+str(curr)
        binanceSpread = str('binance')+str(curr)
        okexSpread = str('okex')+str(curr)
        poloniexSpread = str('poloniex')+str(curr)
    else:
        print('Invalid currency')
        return False


    cexbittrex = cexSpread / bittrexSpread
    cexbinance = binanceSpread / cexSpread
    bittrexbinance = binanceSpread / bittrexSpread
    okexcex = cexSpread / okexSpread
    poloniexcex = poloniexSpread / cexSpread
    bittrexpoloniex = bittrexSpread / poloniexSpread
    poloniexbinance = poloniexSpread / binanceSpread
    poloniexokex = poloniexSpread / okexSpread"""

# create_market_buy_order(self, symbol, amount, params={})
def buyOrder(exchange,symbol,amount):

    def buy_binance(symbol,amount):
        try:
            binanceAPI.create_market_buy_order(symbol,amount)
        except Exception as err:
            print(err)

    def buy_bittrex(symbol,amount):
        try:
            bittrexAPI.create_market_buy_order(symbol,amount)
        except Exception as err:
            print(err)

    def buy_cex(symbol,amount):
        try:
            cexAPI.create_market_buy_order(symbol,amount)
        except Exception as err:
            print(err)

    def buy_okex(symbol,amount):
        try:
            okexAPI.create_market_buy_order(symbol,amount)
        except Exception as err:
            print(err)

    def buy_poloniex(symbol,amount):
        try:
            poloniexAPI.create_market_buy_order(symbol,amount)
        except Exception as err:
            print(err)

    if exchange == 'binance':
        ret = buy_binance(symbol,amount)
        return ret
    elif exchange == 'bittrex':
        ret = buy_bittrex(symbol,amount)
        return ret
    elif exchange == 'cex':
        ret = buy_cex(symbol,amount)
        return ret
    elif exchange == 'okex':
        ret = buy_okex(symbol,amount)
        return ret
    elif exchange == 'poloniex':
        ret = buy_poloniex(symbol,amount)
        return ret
    else:
        print('Invalid Exchange')
        return False


def calcSpreads(currency):

    cexbittrexETH = cexETH / bittrexETH
    cexbinanceETH = binanceETH / cexETH
    bittrexbinanceETH = binanceETH / bittrexETH
    okexcexETH = cexETH / okexETH
    poloniexcexETH = poloniexETH / cexETH
    bittrexpoloniexETH = bittrexETH / poloniexETH
    poloniexbinanceETH = poloniexETH / binanceETH
    poloniexokexETH = poloniexETH / okexETH


    #cexbittrexXMR = cexXMR / bittrexXMR
    #cexbinanceXMR = binanceXMR / cexXMR
    bittrexbinanceXMR = binanceXMR / bittrexXMR
    #okexcexXMR = cexXMR / okexXMR
    #poloniexcexXMR = poloniexXMR / cexXMR
    bittrexpoloniexXMR = bittrexXMR / poloniexXMR
    poloniexbinanceXMR = poloniexXMR / binanceXMR
    poloniexokexXMR = poloniexXMR / okexXMR 

    cexbittrexXRP = cexXRP / bittrexXRP
    cexbinanceXRP = binanceXRP / cexXRP
    bittrexbinanceXRP = binanceXRP / bittrexXRP
    okexcexXRP = cexXRP / okexXRP
    poloniexcexXRP = poloniexXRP / cexXRP
    bittrexpoloniexXRP = bittrexXRP / poloniexXRP
    poloniexbinanceXRP = poloniexXRP / binanceXRP
    poloniexokexXRP = poloniexXRP / okexXRP 

    cexbittrexZEC = cexZEC / bittrexZEC
    cexbinanceZEC = binanceZEC / cexZEC
    bittrexbinanceZEC = binanceZEC / bittrexZEC
    okexcexZEC = cexZEC / okexZEC
    poloniexcexZEC = poloniexZEC / cexZEC
    bittrexpoloniexZEC = bittrexZEC / poloniexZEC
    poloniexbinanceZEC = poloniexZEC / binanceZEC
    poloniexokexZEC = poloniexZEC / okexZEC 

    cexbittrexXLM = cexXLM / bittrexXLM
    cexbinanceXLM = binanceXLM / cexXLM
    bittrexbinanceXLM = binanceXLM / bittrexXLM
    okexcexXLM = cexXLM / okexXLM
    poloniexcexXLM = poloniexXLM / cexXLM
    bittrexpoloniexXLM = bittrexXLM / poloniexXLM
    poloniexbinanceXLM = poloniexXLM / binanceXLM
    poloniexokexXLM = poloniexXLM / okexXLM 

    cexbittrexDASH = cexDASH / bittrexDASH
    cexbinanceDASH = binanceDASH / cexDASH
    bittrexbinanceDASH = binanceDASH / bittrexDASH
    okexcexDASH = cexDASH / okexDASH
    poloniexcexDASH = poloniexDASH / cexDASH
    bittrexpoloniexDASH = bittrexDASH / poloniexDASH
    poloniexbinanceDASH = poloniexDASH / binanceDASH
    poloniexokexDASH = poloniexDASH / okexDASH 

    if currency == 'ETH':
        print(cexbittrexETH)
        print(cexbinanceETH)
        print(bittrexbinanceETH)
        print(okexcexETH)
        print(poloniexcexETH)
        print(bittrexpoloniexETH)
        print(poloniexbinanceETH)
        print(poloniexokexETH)
        cexbittrex = cexbittrexETH
        cexbinance = cexbinanceETH
        bittrexbinance = bittrexbinanceETH
        okexcex = okexcexETH
        poloniexcex = poloniexcexETH
        bittrexpoloniex = bittrexpoloniexETH
        poloniexbinance = poloniexbinanceETH
        poloniexokex = poloniexokexETH

    elif currency == 'DASH':
        print(cexbittrexDASH)
        print(cexbinanceDASH)
        print(bittrexbinanceDASH)
        print(okexcexDASH)
        print(poloniexcexDASH)
        print(bittrexpoloniexDASH)
        print(poloniexbinanceDASH)
        print(poloniexokexDASH)
        cexbittrex = cexbittrexDASH
        cexbinance = cexbinanceDASH 
        bittrexbinance = bittrexbinanceDASH 
        okexcex = okexcexDASH
        poloniexcex = poloniexcexDASH
        bittrexpoloniex = bittrexpoloniexDASH
        poloniexbinance = poloniexbinanceDASH
        poloniexokex = poloniexokexDASH
    elif currency == 'XMR':
        #print(cexbittrexXMR)
        #print(cexbinanceXMR)
        print(bittrexbinanceXMR)
        #print(okexcexXMR)
        #print(poloniexcexXMR)
        print(bittrexpoloniexXMR)
        print(poloniexbinanceXMR)
        print(poloniexokexXMR)
        #cexbittrex = cexbittrexXMR
        #cexbinance = cexbinanceXMR 
        bittrexbinance = bittrexbinanceXMR 
        #okexcex = okexcexXMR
        #poloniexcex = poloniexcexXMR
        bittrexpoloniex = bittrexpoloniexXMR
        poloniexbinance = poloniexbinanceXMR
        poloniexokex = poloniexokexXMR
    elif currency == 'XRP':
        print(cexbittrexXRP)
        print(cexbinanceXRP)
        print(bittrexbinanceXRP)
        print(okexcexXRP)
        print(poloniexcexXRP)
        print(bittrexpoloniexXRP)
        print(poloniexbinanceXRP)
        print(poloniexokexXRP)
        cexbittrex = cexbittrexXRP
        cexbinance = cexbinanceXRP 
        bittrexbinance = bittrexbinanceXRP 
        okexcex = okexcexXRP
        poloniexcex = poloniexcexXRP
        bittrexpoloniex = bittrexpoloniexXRP
        poloniexbinance = poloniexbinanceXRP
        poloniexokex = poloniexokexXRP
    elif currency == 'XLM':
        print(cexbittrexXLM)
        print(cexbinanceXLM)
        print(bittrexbinanceXLM)
        print(okexcexXLM)
        print(poloniexcexXLM)
        print(bittrexpoloniexXLM)
        print(poloniexbinanceXLM)
        print(poloniexokexXLM)
        cexbittrex = cexbittrexXLM
        cexbinance = cexbinanceXLM 
        bittrexbinance = bittrexbinanceXLM 
        okexcex = okexcexXLM
        poloniexcex = poloniexcexXLM
        bittrexpoloniex = bittrexpoloniexXLM
        poloniexbinance = poloniexbinanceXLM
        poloniexokex = poloniexokexXLM

    elif currency == 'ZEC':
        print(cexbittrexZEC)
        print(cexbinanceZEC)
        print(bittrexbinanceZEC)
        print(okexcexZEC)
        print(poloniexcexZEC)
        print(bittrexpoloniexZEC)
        print(poloniexbinanceZEC)
        print(poloniexokexZEC)
        cexbittrex = cexbittrexZEC
        cexbinance = cexbinanceZEC 
        bittrexbinance = bittrexbinanceZEC 
        okexcex = okexcexZEC
        poloniexcex = poloniexcexZEC
        bittrexpoloniex = bittrexpoloniexZEC
        poloniexbinance = poloniexbinanceZEC
        poloniexokex = poloniexokexZEC


    if currency != 'XMR':
        clist = (cexbittrex,cexbinance,bittrexbinance,okexcex,poloniexcex,bittrexpoloniex,poloniexbinance,poloniexokex)
    else:
        clist = (bittrexbinance,bittrexpoloniex,poloniexbinance,poloniexokex)
    cr = len(clist)
    #print(cr)
    average = sum(clist) / int(cr)
    print('Average: '+str(average))



for c in currencies:
    print("\nCurrency: %s\n" % c)
    calcSpreads(c)

