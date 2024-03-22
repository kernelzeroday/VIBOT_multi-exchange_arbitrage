# Notice of publication of source code 2024

Over 5 years have passed since this legacy codebase was last touched, and to my knowledge run in any capacity. I have decided to release this branch of one of the semi complete late stage development versions of this application as an educational resource for those wishing to learn about the concepts contained herein. 

*Beware ye who enter, here be dragons.*


# Vibot Documentation

Vibot is a cryptographic-currency arbitrage trading tool. It works by monitoring for and than exploiting a currency’s price difference between 
multiple currency exchanges, searching for price spreads. When a spreads is detected, a buy order is posted on the lower priced exchange and a sell 
order for same quantity on the higher priced exchanged. This is a form of inter-exchange arbitrage, utilizing a method that eliminates the need for 
transactions, allowing spreads to be quickly closed without waiting for transactions from one exchange to another.

# NOTICE - 9/26/18:

**This repository contains all of the most recent code. Please note that currently, the installation script requires that each server's contents are hosted on a seperate repository.
TODO: Modify installation script to use one unified repository. Also note that the documentation needs to be updated at some point but still is very thorough and sufficient for the time being.**


Vibot consists of multiple components working together via the message queue interface provided by mosquito.

### Scraper / Data Engine
The current data engine is written in GoLang and is called the 'scraper'.

Its arguments are as follows:
```
Usage of ./scraper:
  -currency string
    	space seperated list of currencies to use, default is all (default "USDT_BTC USDT_ETH USDT_XRP USDT_XLM USDT_NEO USDT_DASH USDT_XMR USDT_LSK BTC_ETH BTC_XRP BTC_XLM BTC_NEO BTC_DASH BTC_XMR BTC_LSK BTC_ZEC BTC_LTC BTC_ETC BTC_ADA ETH_ETC ETH_LTC ETH_GNT ETH_OMG BTC_OMG")
  -exchanges string
    	space seperated list of exchanges to use, default is all (default "gdax gemini cex poloniex bittrex bitfinex binance bitstamp")
  -min string
    	minimum spread percentage (default "0.3")
```
To start the scraper, searching for spreads of at least 1% on all supported currency pairs and the exchanges poloniex, bittrex, and cex:

```
./scraper -currency 'BTC_ETH BTC_XRP BTC_XLM BTC_NEO BTC_DASH BTC_XMR BTC_LSK BTC_ZEC BTC_LTC BTC_ETC BTC_ADA ETH_ETC ETH_LTC ETH_GNT ETH_OMG BTC_OMG' -exchanges 'poloniex bittrex cex' -min 0.1
```
After initialization, when a spread is detected, you will see the output in this format, and a message will be sent with the spread over mqtt to the topic /spread/BTC_OMG
```
2018/03/23 22:18:18 /spread/BTC_OMG: [{"Name":"BTC_OMG_bittrex_poloniex","BuyFrom":"bittrex","SellTo":"poloniex","BuyFee":0.0025,"SellFee":0.0025,"BuyPrice":0.00125212,"BuyQty":150,"SellPrice":0.00126002,"SellQty":0.30958098,"Value":0.1290300429,"EMA":0.0540834998,"EMVAR":0.0101542488,"Score":0.196215685,"Count":1,"EMARate":0.0000375939849624,"EMAMaxPos":0,"EMAAge":940560146400.80884,"TimeStart":1521843498471,"TimeLast":0,"LastUpdate":1521843498471636625,"Type":"transient"}]```
```
This json object can be unrolled using `jq` to see the object in a more readable format like so:
```
 echo ['{"Name":"BTC_OMG_bittrex_poloniex","BuyFrom":"bittrex","SellTo":"poloniex","BuyFee":0.0025,"SellFee":0.0025,"BuyPrice":0.00125212,"BuyQty":150,"SellPrice":0.00126002,"SellQty":0.30958098,"Value":0.1290300429,"EMA":0.0540834998,"EMVAR":0.0101542488,"Score":0.196215685,"Count":1,"EMARate":0.0000375939849624,"EMAMaxPos":0,"EMAAge":940560146400.80884,"TimeStart":1521843498471,"TimeLast":0,"LastUpdate":1521843498471636625,"Type":"transient"}]'|jq
[
  {
    "Name": "BTC_OMG_bittrex_poloniex",
    "BuyFrom": "bittrex",
    "SellTo": "poloniex",
    "BuyFee": 0.0025,
    "SellFee": 0.0025,
    "BuyPrice": 0.00125212,
    "BuyQty": 150,
    "SellPrice": 0.00126002,
    "SellQty": 0.30958098,
    "Value": 0.1290300429,
    "EMA": 0.0540834998,
    "EMVAR": 0.0101542488,
    "Score": 0.196215685,
    "Count": 1,
    "EMARate": 3.75939849624e-05,
    "EMAMaxPos": 0,
    "EMAAge": 940560146400.8088,
    "TimeStart": 1521843498471,
    "TimeLast": 0,
    "LastUpdate": 1521843498471636700,
    "Type": "transient"
  }
]
```

Each field shows a different value, the most important being the Value field, which shows the value of the price spread. EMA calculation, spread count, and Type are also fields of interests. Spreads will be marked as 'Transient' or 'Steady' depending on how many of them appear in the orderbooks.

The current bid and ask prices are available for examination along with the currency pair.

### Trade Engine
The next component is the trade engine. This piece takes in the available data from the data engine and calculates arbitrage opportunity. It is written in python, and takes no arguments. At startup, it will calculate all of the target hedge ratios (based on market cap), and than update the balances of the exchanges, which come the balance engine. 
```
ubuntu@ip-172-31-21-170:~/trade$ ./trade_current.py
bittrex: Assigned hedge remainder (0.09%) randomly to BTC_OMG
cex: Assigned hedge remainder (0.04%) randomly to BTC_XRP
poloniex: Assigned hedge remainder (0.09%) randomly to BTC_LTC
bittrex	- BTC_XRP	11.87 %
bittrex	- BTC_ETH	17.13 %
bittrex	- BTC_DASH	2.61 %
bittrex	- BTC_ZEC	2.92 %
bittrex	- BTC_XLM	10.11 %
bittrex	- BTC_LTC	5.41 %
bittrex	- BTC_ETC	3.83 %
bittrex	- BTC_XMR	3.63 %
bittrex	- BTC_OMG	2.58 %
bittrex	- BTC_LSK	2.54 %
bittrex	- BTC_XEM	12.20 %
bittrex	- ETH_ETC	8.21 %
bittrex	- ETH_GNT	1.27 %
bittrex	- ETH_OMG	6.00 %
bittrex	- ETH_ZRX	0.00 %
bittrex	- BTC_REP	0.69 %
bittrex	- BTC_RDD	3.90 %
bittrex	- BTC_SC	4.69 %
bittrex	- BTC_ZRX	0.41 %
bittrex	- TOTAL BTC:	4182.18049125 (56.27 %)
cex	- BTC_XRP	29.81 %
cex	- BTC_ETH	50.60 %
cex	- BTC_DASH	4.59 %
cex	- BTC_ZEC	2.53 %
cex	- BTC_XLM	12.47 %
cex	- TOTAL BTC:	58.53572106 (0.78 %)
poloniex	- BTC_XRP	12.31 %
poloniex	- BTC_ETH	21.47 %
poloniex	- BTC_DASH	2.80 %
poloniex	- BTC_ZEC	2.66 %
poloniex	- BTC_XLM	12.83 %
poloniex	- BTC_LTC	4.77 %
poloniex	- BTC_ETC	5.34 %
poloniex	- BTC_XMR	10.81 %
poloniex	- BTC_OMG	0.62 %
poloniex	- BTC_LSK	5.56 %
poloniex	- BTC_XEM	6.44 %
poloniex	- ETH_ETC	6.30 %
poloniex	- ETH_GNT	1.19 %
poloniex	- ETH_OMG	1.22 %
poloniex	- ETH_ZRX	3.07 %
poloniex	- BTC_REP	0.13 %
poloniex	- BTC_RDD	0.00 %
poloniex	- BTC_SC	1.72 %
poloniex	- BTC_ZRX	0.76 %
poloniex	- TOTAL BTC:	3191.36305893 (42.94 %)
Connected Successfully
Updated cex BTC Balance to: 0.00005768 Available, 0.0 Pending, 0.00005768 Total
Updated cex ETH Balance to: 0.0 Available, 24.66494 Pending, 24.66494 Total
Updated cex DASH Balance to: 6.7138296 Available, 1.958 Pending, 8.6718296 Total
Updated cex ZEC Balance to: 0.0 Available, 43.49651271 Pending, 43.49651271 Total
Updated cex XRP Balance to: 0.0 Available, 14500.302876 Pending, 14500.302876 Total
Updated cex XLM Balance to: 0.0 Available, 20198.3213668 Pending, 20198.3213668 Total
```

When a trade opportunity is detected it will create a 'trade' object and pass it to the the `verified` topic on the message queue for consumption by the order tracking engine. After a successful trade, and depending on the current hedge ratios, a buyback and/or sellback order will be posted, which will expire between 150-300 seconds from post time. The order tracking engine will cancel this order, unless it is considered 'viable', (viable means the price difference between the target and current price of the order is within a certain configurable threashold. Arbitrage orders expire immediatly if not filled. Limit orders will be canceled 1-3 minutes later if not filled.

Before running the trade engine, edit the variable `net` in the file `config.py`, which contains the API keys and other required information for operation. The net variable should reflect the total balance of all exchanges and is used to calculate the hedge allocations for ORDERBACK orders.


An example trade opportunity object looks like this:
```
{"Exchange": "bittrex", "Pair": "ETH-OMG", "Kind": "Arbitrage", "Type": "sell", "OrderID": "558b49c3-95de-4da2-8082-c3988193feb2", "Price": "0.02101841", "Qty": "1.0000", "Timestamp": 1521838358.7188723, "Expires": 0}
```
or unpacked json:
```
{
  "Exchange": "bittrex",
  "Pair": "ETH-OMG",
  "Kind": "Arbitrage",
  "Type": "sell",
  "OrderID": "558b49c3-95de-4da2-8082-c3988193feb2",
  "Price": "0.02101841",
  "Qty": "1.0000",
  "Timestamp": 1521838358.7188723,
  "Expires": 0
}


```


Visible is the currency spread detected as well as the price and amount along with the direction.

The trade engine configuation is found in the file config.py like so:
```
net='230' # total btc (TODO: automate this so it does not need to be user set)
mq_host = 'localhost'
mq_port = 1883
mq_keepalive = 60
mq_bindAddress = ""
mq_user = 'vibot'
mq_pass = ''
mq_subtop = 'trade'
mq_subtop_pbal = 'pbal'
mq_subtop_cbal = 'cbal'
mq_pubtop = 'messages'

poloniexKey = ''
poloniexSecret = ''
cexUser = ''
cexKey = ''
cexSecret = ''
bittrexKey = ''
bittrexSecret = ''

```
The currency pairs need to be defined in the file pairInfo.py, which holds all of the required information about the pairs in this format:

```
    "BTC_ZEC":  {
        "name": "BTC-ZEC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "qtyval",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "BTC-XLM",
        "base": "BTC",
        "quote": "XLM",
        "minType": "qtyval",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },

    "BTC_DASH": {
        "name": "DASH/BTC",
        "base": "BTC",
        "quote": "DASH",
        "minType": "qty",
        "minQty": Decimal('0.015'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },

    "BTC_ETC": {
        "name": "BTC_ETC",
        "base": "BTC",
        "quote": "ETC",
        "minType": "val",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),

```
Important to note are the quantity minimums of each currency on each exchange. The minimum can be set using the value `qty` for calculation using a static quantity, `val` to calculate based on BTC (or base currency) value, or `qtyval`, which is a combination of the two.


### MqTT Data Streams

Vibot is driven by a protocol called MqTT, or “the Message Queuing Telemetry Transport”. MQTT was first developed for trading on the stock market. It is very fast, reliable, and allows us access to a stream of live data.


Configure these settings to match the configuration of the message queue (mosquito) and it will be active to make trades.
To see the output, subscript to the topic `messages`:
```
ubuntu@ip-172-31-21-170:~$ mosquitto_sub -u vibot -P <password> -t messages -h localhost -p 1883
```

for the sake of simplification, a pair of  shell wrapper scripts exist with the mqtt credentials hardcoded:
```
#!/bin/bash
##########
# Shell wrapper script for securing mosquitto (subscriptions)

password='NmQ5Nj_3MrAwiNDu'
mosquitto_sub -u vibot -P "$password" "$@"
```

You can use the wrapper script `/usr/local/bin/sub` like so to see the output from the buysell engine:
```
ubuntu@ip-172-31-21-170:~$ sub -t messages
```

Simularly, you can subscribe to watch the current ticker data,or spread data by subscribing to the topics `/ticker/#` and `/spread/#`:

Spread stream:
```
ubuntu@ip-172-31-21-170:~$ sub -t /spread/#

[{"Name":"BTC_XEM_bittrex_poloniex","BuyFrom":"bittrex","SellTo":"poloniex","BuyFee":0.0025,"SellFee":0.0025,"BuyPrice":0.00003116,"BuyQty":11206.521,"SellPrice":0.00003169,"SellQty":1951.25333737,"Value":1.193662186,"EMA":1.1678238702,"EMVAR":0.0034360535,"Score":0.0676466535,"Count":202,"EMARate":0,"EMAMaxPos":264999.9999785457,"EMAAge":1521843950848.9071509764,"TimeStart":1521843953762,"TimeLast":0,"LastUpdate":1521844192512483604,"Type":"steady"}]
[{"Name":"BTC_XLM_bittrex_poloniex","BuyFrom":"bittrex","SellTo":"poloniex","BuyFee":0.0025,"SellFee":0.0025,"BuyPrice":0.0000269,"BuyQty":162.04732619,"SellPrice":0.00002707,"SellQty":289.65029181,"Value":0.1300651716,"EMA":0.0624613569,"EMVAR":0.0396541051,"Score":0.1769918701,"Count":101,"EMARate":0.0000003484,"EMAMaxPos":0,"EMAAge":1521681421287.7494535107,"TimeStart":1521844183012,"TimeLast":0,"LastUpdate":1521844193012482666,"Type":"transient"}]
```

Ticker Stream:

```
sub -t /ticker/#|jq
{
  "bittrex": {
    "Name": "USD_XMR_bittrex",
    "Pair": "USD_XMR",
    "Exchange": "bittrex",
    "LastUpdate": 1521844248131439400,
    "MinAsk": {
      "Key": "209.68",
      "Price": 209.68,
      "Qty": 6.6455,
      "Timestamp": 1521814353540098600
    },
    "MaxBid": {
      "Key": "211.21139949",
      "Price": 211.21139949,
      "Qty": 4.57973783,
      "Timestamp": 1521815923162880300
    }
  },
  "poloniex": {
    "Name": "USD_XMR_poloniex",
    "Pair": "USD_XMR",
    "Exchange": "poloniex",
    "LastUpdate": 1521844249727063000,
    "MinAsk": {
      "Key": "209.8529877",
      "Price": 209.8529877,
      "Qty": 43.79092725,
      "Timestamp": 1521843755039540200
    },
    "MaxBid": {
      "Key": "211.1483832",
      "Price": 211.1483832,
      "Qty": 75.447,
      "Timestamp": 1521821621551787800
    }
  }
}


```



```

To publish messaes, use mosquitto_pub:

ubuntu@ip-172-31-21-170:~$ mosquitto_pub -u vibot -P <password> -h localhost -p 1883 -t messages -m "hello, world!"
```

or use the wrapper script called pub (for simplification):
```
ubuntu@ip-172-31-21-170:~$ pub -t messages -m "hello, world!"
```

### Engines



Multiple engines can be run in parallel on multiple servers. The exchanges rate limit REST api calls (typically 6 per second), so an optimal setup will require one server to retrieve ticker data for each 
currency pair the user wants to monitor, and another server to analyses all of the data and execute the actual trades. 
However, the engine CAN run on a single machine for a single pair without issues. Should rate limiting occur, it will be resolved automatically after a given period, and does not result in a permanent ban.

## Extra Tools




Additionally, tools are provided to interact with the exchanges manually via cextool and polotool.

Tools to interact with more exchanges are currently being developed. 

Note: the polotool depends on python3.6 , specifically. I have installed it.


```

Poloniex Tool Options:

usage: polotool [-h] [-c CONFIG] [-p PAIR] [-B] [-A] [-H] [-g GEN_ADDR] [-ii]
                [-t] [-F] [-b] [-s] [-a AMOUNT] [-P PRICE] [-o] [-C] [-m]
                [-i ORDER_ID] [-S SINCE] [-w] [-W WALLET_ADDRESS]
                [-X CURRENCY] [-I PAYMENT_ID] [-D] [-d]

Poloniex API Tool

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        config .cfg file
  -p PAIR, --pair PAIR  Get ticker information for this pair (example:
                        BTC_ETH)
  -B, --balances        Get available balances
  -A, --all_balance     Get all balance data
  -H, --history         print market history data for given pair ,specify w -p
  -g GEN_ADDR, --gen_addr GEN_ADDR
                        Generate a new deposite address for supplied currency
                        (example: BTC)
  -ii, --info           Return currency info
  -t, --ticker          Get ticker information for pai , specify with -p
                        (default: BTC_ETH)
  -F, --fee             Get fee info for account
  -b, --buy             Buy
  -s, --sell            Sell
  -a AMOUNT, --amount AMOUNT
                        Amount to buy or sell
  -P PRICE, --price PRICE
                        Price to buy or sell at
  -o, --orders          Return open orders
  -C, --cancel_order    Cancel an order
  -m, --move_order      Move an order
  -i ORDER_ID, --order_id ORDER_ID
                        Cancel an order
  -S SINCE, --since SINCE
                        Time - this
  -w, --withdraw        Withdraw currency [specify wallet_address (-W) ,
                        amount (-a), and currency (-X) ]
  -W WALLET_ADDRESS, --wallet_address WALLET_ADDRESS
                        Withraw to this address [example:
                        15isHXhXV85i7QFwwwed9gg9ET5mWjNppP ]
  -X CURRENCY, --currency CURRENCY
                        Withdraw this currency [example: BTC]
  -I PAYMENT_ID, --payment_id PAYMENT_ID
                        Payment ID for XMR type withdrawals
  -D, --deposit_addresses
                        Return account deposit addresses
  -d, --deposit_history
                        Return deposit history
```

To grab ticker data, the syntax is:
```
./polotool -t -p USDT_BTC 
```

To grab balance data, the syntax is 
```
./polotool -B
```

I usually pipe it to jq for readability:
```
./polotool -B|jq
{
  "exchange": {
    "BTC": "1.06424756",
    "ETC": "0.19950000",
    "USDT": "19.09861795",
    "XRP": "0.98500000",
    "ZEC": "96.27842836"
  }
}
```

To place a buy or sell order, you must specify an amount, pair, and price:

(example: buy 1 eth at 0.045 btc) 
```
./polotool -b -p BTC_ETH -a 1.0 -P 0.045 
```

same with sell:
(example: sell 1 eth at 0.045 btc) 
```
./polotool -s -p BTC_ETH -a 1.0 -P 0.045 
```

The other functions are relatively self explanatory and also are mostly  compatable with the cextool:

CexIO Api Tool usage:
```
usage: cextool [-h] [-p PAIR] [-P PRICE] [-a AMOUNT] [-c] [-C] [-i ORDER_ID]
               [-F] [-O] [-b] [-s] [-B] [-o] [-t] [-T] [-S] [-G] [-X CURRENCY]

CexIO API Tool

optional arguments:
  -h, --help            show this help message and exit
  -p PAIR, --pair PAIR  buy or sell this currency pair (example: BTC_ETH)
  -P PRICE, --price PRICE
                        at this price (example: 0.011)
  -a AMOUNT, --amount AMOUNT
                        for this amount (example: 0.5)
  -c, --convert         Convert a crypto to fiat. Specify with <-p/--pair>
                        <-a/--amount>
  -C, --cancel_order    Cancel an order with specified order id [ -i
                        <order_id>]
  -i ORDER_ID, --order_id ORDER_ID
                        Order ID Number
  -F, --fee_info        Fee info for this account
  -O, --current_orders  Get current orders for specified pair (with -p)
  -b, --buy             Submit a buy order
  -s, --sell            Submit a sell order
  -B, --balance         Get account balances (example: BTC)
  -o, --order_book      Return order book for given currency pair (specify
                        with -p) (example: BTC/USD)
  -t, --ticker          Return ticker data for pair (specify with -p)
  -T, --ticker_loop     Continueously return ticker data for this pair
                        (specify with -p)
  -S, --price_stat      Retrieve price statistics for last 24 hours for a
                        given pair (specify with -p)
  -G, --get_deposit_address
                        Return deposit address for currency [specify with -X]
  -X CURRENCY, --currency CURRENCY
                        Specify a currency

```


Bittrex Tool Usage


```


ubuntu@ip-172-31-21-170:~$ ./bittrextool -h
usage: bittrextool [-h] [-f CONFIG] [-t] [-d] [-V] [-D] [-B] [-k] [-b] [-s]
                   [-C] [-m] [-S] [-W] [-w] [-O] [-o] [-T ORDER_TYPE] [-I]
                   [-H] [-q] [-c CURRENCY] [-p PAIR] [-i ORDER_ID]
                   [-A ADDRESS] [-x COUNT] [-a AMOUNT] [-P PRICE]

Bittrex API Tool

optional arguments:
  -h, --help            show this help message and exit
  -f CONFIG, --config CONFIG
                        config .cfg file
  -t, --ticker          Get ticker information for pai , specify with -p
                        (example: BTC-ETH)
  -d, --deposit_address
                        Get deposit addresses for currency (specify with -c)
  -V, --verbose         Enable extra verbose messages for debugging
  -D, --deposit_history
                        Return acct deposit history
  -B, --balances        Get all available balances
  -k, --balance         Get a particular account balance (specifiy with -c)
  -b, --buy_limit       Buy Limit Order
  -s, --sell_limit      Sell Limit Order
  -C, --cancel_order    Cancel an order
  -m, --buy_market      Buy at market price
  -S, --sell_market     Sell at market price
  -W, --withdraw        DANGEROUS: Withdraw (specify currency <-c>, amount
                        <-a>, and address <-A>)
  -w, --withdrawal_history
                        Get withdrawl history (specify currency <-c> , and
                        optionally count <-x>)
  -O, --open_orders     Get open orders for pair (specify with -p)
  -o, --order_book      Retreive order book for pair
  -T ORDER_TYPE, --order_type ORDER_TYPE
                        Specify "buy", "sell", or "both"
  -I, --currencies      Return a list of supported currency information
  -H, --order_history   Return your order history
  -q, --order_status_query
                        Query an order by uuid for status
  -c CURRENCY, --currency CURRENCY
                        Specify a currency (example: BTC)
  -p PAIR, --pair PAIR  Specify a currency pair (example: BTC_ETH)
  -i ORDER_ID, --order_id ORDER_ID
                        Specify an order id
  -A ADDRESS, --address ADDRESS
                        Specify a crypto wallet address for withdrawal
                        (example: 15isHXhXV85i7QFwwwed9gg9ET5mWjNppP
  -x COUNT, --count COUNT
                        Specify a count <for depth>
  -a AMOUNT, --amount AMOUNT
                        Specify an amount to buy, sell, withdraw, etc
  -P PRICE, --price PRICE
                        Price to buy or sell at

```

Data can always be piped to jq, as both programs always output valid json.

### Profit Calculation

When doing arbitrage between mutiple exchanges, calculating gains and losses can be confusing. Essentially, the idea is that we add all of the balances
of all of the coins in all of the exchanges, and multiply each balance by the bid price on the corresponding exchange. 

```
ubuntu@ip-172-31-21-170:~/trade$ ./balanceCalc_current.py
BITTREX
BITTREX TOTAL: 0.000000

CEX
CEX TOTAL: 0.000000

POLONIEX
POLONIEX TOTAL: 0.000000

TOTAL BTC: 0.000000

BITTREX
BITTREX TOTAL: 0.000000

CEX
BTC {'available': 5.768e-05, 'pending': 0.0, 'value': 5.768e-05}
ETH {'available': 0.0, 'pending': 24.66494, 'value': 1.53438125246}
DASH {'available': 6.7138296, 'pending': 1.958, 'value': 0.42058373560000006}
ZEC {'available': 0.0, 'pending': 43.49651271, 'value': 1.26139886859}
XRP {'available': 0.0, 'pending': 14500.302876, 'value': 1.04967692519364}
XLM {'available': 0.0, 'pending': 20198.3213668, 'value': 0.543940794407924}
CEX TOTAL: 4.810039

POLONIEX
POLONIEX TOTAL: 0.000000

TOTAL BTC: 4.810039
```

### Order Tracking Engine

The order tracking engine is responcible for canceling orders that do not fill so that capitol is always available for future trades. 
It takes no arguments and can be started with ./OrderTrack.py . The output looks as follows:
```
[*] Order 667c582b-3484-4dc2-bfa4-5c64585db19c on exchange bittrex qued in thread for canceling
[i] Ticker call...0.02100965
[i] DEBUG: buy 0.02086071 0.02100965
[i] Pct was: 0.7139737813334263
[i] Ticker call...0.02086071
[i] DEBUG: sell 0.02101841 0.02086071
[i] Pct was: 0.7502946226665108
[i] Ticker call...0.02086071
[i] DEBUG: sell 0.02101841 0.02086071
[i] Pct was: 0.7502946226665108
[*] Successfully canceled order b76b4537-b27c-44e1-9149-481400118a57
[*] Successfully canceled order a19253c3-0a1c-49bf-89e7-1a6fe3758710
[*] Successfully canceled order beac29d0-77c6-45dc-a23d-139b5e27aa79
Arb order
[*] Order 6425807b-b89b-463d-beac-ee1d449831a0 on exchange bittrex qued in thread for canceling
Arb order
[*] Order b74a6a1c-72b1-4a80-88a2-3aeb605ec584 on exchange bittrex qued in thread for canceling
Arb order
[*] Order 9c56422e-bbc7-4c25-8810-083d70c0252b on exchange bittrex qued in thread for canceling
Arb order
[*] Order b7f267f3-e50a-4625-a1c2-bc692e0cf109 on exchange bittrex qued in thread for canceling
[i] Ticker call...0.02086071
```


### Transfer Engine

The transfer engine is responcible for accepting json messages over mqtt with instrucutions for processing withdrawals. It can also be used manually from the command line. It's arguments are as follows:

```
ubuntu@ip-172-31-30-189:~/transfer_engine$ ./transfer.py -h
[*] ARGV      : ['-h']
Usage: transfer.py [options]

Options:
  -h, --help            show this help message and exit
  -w, --withdraw        
  -e EXCHANGE, --exchange=EXCHANGE
  -d DEPOSIT_EXCHANGE, --deposit_exchange=DEPOSIT_EXCHANGE
  -c CURRENCY, --currency=CURRENCY
  -q QUANTITY, --quantity=QUANTITY
  -g, --get_address     
  -s, --safe            
  -l, --live            
  -m, --mqttd           

```

Because of the risk involved in transactions, it was written to only accept exchanges (from exchange, to exchange) as arguments. It than will query the exchanges API for the correct deposit 
address of the "to exchange", and initate the transfer. Note: Some currencies require an additional field, called either the "memo", "payment id", or "message". These currencies, such as XMR, 
XRP, and XLM have *hardcoded* addresses and payment ids, which are present in the transfer engine's library, 'transferlib_py', in the /lib directory.

When processing a transfer request, the output will show as follows:


```

action: transfer , Currency: XEM, Amount: 130000, From: bittrex, To: poloniex     

```
continued...

```
[!] Warn: New XEM Withdrawal functionality requested. Please monitor closely for success.
[*] XEM Withdrawl requested
[!] Warning: attempting new payment id functionality...
{"uuid": "92035b89-72ec-4300-8c90-5dcb53da2cbf"}
Currency:XEM
Amount :130000
Address: NBZMQO7ZPBYNBDUR7F75MAKA2S3DHDCIFG775N3D
INFO: Payment id bb09c990417da001 specified
DEBUG: Transfer Engine:None
{"action":"transfer","currency":"LSK","amount":320.02304165899943,"from":"poloniex","to":"bittrex"}
Action: transfer , Currency: LSK, Amount: 320.02304165899943, From: poloniex, To: bittrex 
Standard withdrawal requested
[*] 9636347135434721277L
{"response": "Withdrew 320.02304165 LSK."}
Currency:LSK
Amount :320.02304165899943
Address: 9636347135434721277L
```
Transfers are calculated by the asset managment engine (called asset.rb), which searches for empty wallets and sends a transfer request when it is determined that a movement is necessary. 
There is also a manual transfer tool called mqTransfer.py. It can be used with cli arguments or interactively, specificying the -i flag. It's arguments are as follows:

```


ubuntu@ip-172-31-21-170:~$ ./mqTransfer.py -h
Warning: Live Mode Enabled!
[*] ARGV      : ['-h']
Usage: mqTransfer.py [options]

Options:
  -h, --help            show this help message and exit
  -i, --interactive     
  -m, --mqttd           
  -c CURRENCY, --currency=CURRENCY
  -q QUANTITY, --quantity=QUANTITY
  -f FROM_EXCHANGE, --from=FROM_EXCHANGE
  -t TO_EXCHANGE, --to=TO_EXCHANGE
ubuntu@ip-172-31-21-170:~$ 

```



Interactive mode:



```
ubuntu@ip-172-31-21-170:~$ ./mqTransfer.py -i
Warning: Live Mode Enabled!
[*] ARGV      : ['-i']
Manual Funds Mangement Client: 
>> Currency: BTC
>> Quantity: 1
>> From Exchange: poloniex
>> To Exchange: cex
Message: {"action":"transfer","currency":"BTC","amount":1,"from":"poloniex","to":"cex"}
Send? y/n :

```
Non interactive mode:

```
./mqTransfer.py -c BTC -q 1 -f poloniex -t cex
```

This tool takes user input and creates a transfer request json object, which is than sent to the server which is running the transfer receiver.

### Balance Engine

The balance engine streams balance data to the main server (where the trade engine is running). The trade engine requires a constant stream of balance data to 
operate, because trade must not be proccessed if the correct balances are not present. 

```

ubuntu@ip-172-31-21-234:~/balance_engine$ ./start.sh
Starting streams...
ubuntu@ip-172-31-21-234:~/balance_engine$ Starting cex balance stream
Starting poloniex balance stream
Starting bittrex balance stream.

```

### MqIRC - IRC Monitoring Interface

MqIRC is an mqtt to irc proxy, which allows for easy monitoring of the bot's status. To start it , run



```
./mqirc
```





Built in bot controls can seen by running `@help`:




```
18:46 <@mqirc> ======== MQIRC Version 2.2 BetaBot Commands ========
18:46 <@mqirc> Bot responds to the following commands
18:46 <@mqirc> @cmd :<message> Send a message to pubtopic
18:46 <@mqirc> @help :  Show this help
18:46 <@mqirc> @die :  Shut down bot
18:46 <@mqirc> @echo : <string>  Echo a message
18:46 <@mqirc> @shell : <command>  Execute shell a command locally
18:46 <@mqirc> ======= Authentication Commands ========
18:46 <@mqirc> @enable : <password> : Authenticate to and enable the boT
18:46 <@mqirc> @disable : <password> : Lock bot. When disabled will only respond to @help
18:46 <@mqirc> @userlist :Send list of authorized senders
18:46 <@mqirc> @adduser : <user/#channel> : Append nick/channel to authorized senders
18:46 <@mqirc> @deluser : <user/#channel> : Remove nick/channel from authorized senders
18:46 <@mqirc> ======== IRC Commands ========
18:46 <@mqirc> @irc :<command> : Send a raw irc command to server
18:46 <@mqirc> @register :<password> <email> Register bot with nickserv
18:46 <@mqirc> @join :<channel> Join this channel
18:46 <@mqirc> @part :<channel> Leave this channel
18:46 <@mqirc> ======== ========= ========
```

All commands are prefixed with an `@` . 


### Balance Reporting Engine

A cronjob automatically sends a balance report to the bot's user every hour. No interaction is required, simply enable the cron job by uncommenting it in the cron task list:

```
$ crontab -e

#@hourly /home/ubuntu/hourly-bal.sh

```

The email addresses of the recipitents are stored in the file sendmail.py, which can be used interactively as well. :

```
ubuntu@ip-172-31-21-170:~$ ./sendmail.py -h
usage: sendmail.py [-h] [-f SEND] [-r RECV] [-m MESSAGE] [-S SUBJECT]
                   [-s SERVER]

optional arguments:
  -h, --help            show this help message and exit
  -f SEND, --send SEND  Sender of this message.
  -r RECV, --recv RECV  Recipitent of this message.
  -m MESSAGE, --message MESSAGE
                        File containing message content to send.
  -S SUBJECT, --subject SUBJECT
                        Subject of email to send.
  -s SERVER, --server SERVER
                        Hostname or ip of the smtp server to use.


```
### Log Engine

The log engine simply logs each trade as they come through the `verified` stream. To start it, simply run ./log.py . Trades are logged to 
the file trade.log.


### 




### Other Notes

Vibot is very complex system consisting of multiple components. Because API calls to currency exchanges are often rate limited, it is a good idea to run certain engines on 
different servers. The scraper and trade engine should be run on the same server, to reduce latency, as the scraper uses the websocket streams, while the trade engine uses
the rest api, which are limited seperatly. 

The balance engine should run a different server because it queries the balances of all exchanges at least once per second, and thus uses many API calls.

The transfer engine should be run a secure, dedicated server. Although it does not use too many API calls, for security reasons, it should run in an isolated environment.

The Order Tracking engine definitly needs to run on it's own server because it uses many api calls when canceling orders and calculating viability. 


If you have any questions, feel free to contact the developers of Vibot at xelectron@protonmail.com. 
