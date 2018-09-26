# Vi1

## Main Server - Scraper, Trade, Log engines, irc proxy, exchange api tools


### Usage:

To start the scraper:

    cd scraper
    ./scraper -min 0.01 -exchanges 'cex poloniex bittrex binance okex' -currency 'BTC_ETH BTC_XRP BTC_XLM BTC_DASH BTC_XMR BTC_ZEC'


min: Minimum spread (as percentage, 0.01 = 1% profit [ including exchange commision fees, these are calculated into the spread ]
exchanges: which exchanges to use
currency: currency pairs to trade


To start the Order Engine:

    cd order_engine
    ./Trade.py

