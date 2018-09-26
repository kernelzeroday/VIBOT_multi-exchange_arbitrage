# Tranfer Engine Documentation


## Preface

The transfer engine manages deposites between exchanges autmatically. The is a WIP.

## Components

`transfer_engine.py` - Utility to mange obtaining deposit addresses and processing withdrawals.

<pre>

ARGV      : ['-h']
Usage: transfer_engine.py [options]

Options:
  -h, --help            show this help message and exit
  -w, --withdraw        # initiate a withdrawal
  -e EXCHANGE, --exchange=EXCHANGE # withdraw from this exchange
  -d DEPOSIT_EXCHANGE, --deposit_exchange=DEPOSIT_EXCHANGE # deposit into this exchange
  -c CURRENCY, --currency=CURRENCY # withdraw this currency (ex: BTC) NOTE: currencies requiring payment ids are not yet supported
  -q QUANTITY, --quantity=QUANTITY # move this quantity
  -g, --get_address     # Simply return a deposit address, do not withdraw
  -s, --safe            # Safe mode - require user interaction
  -l, --live            # Specify this flag for live mode

</pre>

MqTT Listen mode:

<pre>
Send a message to topic `transfers` as follows:

{
    "action": "transfer",
    "amount": "1",
    "currency": "BTC",
    "from": "poloniex",
    "to": "cex"
}

echo '{"action":"transfer","amount":"1","currency":"LTC","from":"poloniex","to":"bittrex"}'|mosquitto_pub -t transfers/incoming -s

</pre>

Grab a deposit address:
<pre>

$ ./transfer_engine.py -g -d cex -c ETH
ARGV      : ['-g', '-d', 'cex', '-c', 'ETH']
Withdraw Exchange : bittrex
Deposit Exchange:  cex
Currency :  ETH
Quantity: 0.0
Notice: demo mode, will not actually withdraw.
Exchange : bittrex
Currency :  ETH
Quantity: 0.0
Grabbing deposit address
0x3398e2fe59929b27ee550f1f8ee26e3ee2ef8604

</pre>

Initate a withdrawal:

<pre>

ARGV      : ['-w', '-d', 'poloniex', '-e', 'bittrex', '-c', 'DASH', '-q', '1', '-s', '-l']
Withdraw Exchange : bittrex
Deposit Exchange:  poloniex
Currency :  DASH
Quantity: 1.0
Warning: live mode enabled!
Withdrawal requested.
Safe mode enabled.
Exchange : bittrex
Currency :  DASH
Quantity: 1.0
Withdrawal requested : bittrex > poloniex
Getting adderess for poloniex ...
Address for DASH on poloniex is: XjUicVdp4pk3n1qm1yLZRY6ZnLTjH7JpKo
Live: 0 Withdraw from: bittrex Deposit into: poloniex Currency: DASH Quantity: 1.0 Address: XjUicVdp4pk3n1qm1yLZRY6ZnLTjH7JpKo , procceed (YES/No): YES
{"uuid": "7033e068-c1b7-4c6c-b6db-5a7221b5cc1e"} # <--- This means success
Currency:DASH
Amount :1.0
Address: XjUicVdp4pk3n1qm1yLZRY6ZnLTjH7JpKo

</pre>


Wait a moment and than you can confirm with bittrex api:

<pre>

[
  {
    "PaymentUuid": "7033e068-c1b7-4c6c-b6db-5a7221b5cc1e",
    "Currency": "DASH",
    "Amount": 0.998,
    "Address": "XjUicVdp4pk3n1qm1yLZRY6ZnLTjH7JpKo",
    "Opened": "2018-02-25T01:44:23.787",
    "Authorized": true,
    "PendingPayment": false,
    "TxCost": 0.002,
    "TxId": "0c7d071d1df6e96b9317255daa369862ed5653bfffac6c56cb161aae3db67a58",
    "Canceled": false,
    "InvalidAddress": false
  }

</pre>


`hedge.py` - Utility that publishes recommended hedge allocations (as per market cap) to topic `hedge` and stdout
Also calculates total volume of each exchange, which may be taken into consideration when calculating movements.
<pre>


$ ./hedge.py
BTRX: Assigned hedge remainder (0.07%) randomly to BTC_LTC
CEX: Assigned hedge remainder (0.02%) randomly to BTC_DASH
POLX: Assigned hedge remainder (0.03%) randomly to BTC_XRP
{"exchange" : "BTRX", "pair" : "BTC_XRP", "ratio" : "8.30"}
{"exchange" : "BTRX", "pair" : "BTC_ETH", "ratio" : "16.13"}
{"exchange" : "BTRX", "pair" : "BTC_DASH", "ratio" : "1.95"}
{"exchange" : "BTRX", "pair" : "BTC_ZEC", "ratio" : "2.39"}
{"exchange" : "BTRX", "pair" : "BTC_XLM", "ratio" : "6.59"}
{"exchange" : "BTRX", "pair" : "BTC_LTC", "ratio" : "15.50"}
{"exchange" : "BTRX", "pair" : "BTC_LSK", "ratio" : "5.02"}
{"exchange" : "BTRX", "pair" : "BTC_ETC", "ratio" : "41.06"}
{"exchange" : "BTRX", "pair" : "BTC_XMR", "ratio" : "3.06"}
BTRX	- TOTAL BTC:	5734.91976402 (50.92 %)
{"exchange" : "CEX", "pair" : "BTC_XRP", "ratio" : "36.00"}
{"exchange" : "CEX", "pair" : "BTC_ETH", "ratio" : "40.94"}
{"exchange" : "CEX", "pair" : "BTC_DASH", "ratio" : "3.16"}
{"exchange" : "CEX", "pair" : "BTC_ZEC", "ratio" : "1.18"}
{"exchange" : "CEX", "pair" : "BTC_XLM", "ratio" : "18.72"}
CEX	- TOTAL BTC:	79.67804367 (0.70 %)
{"exchange" : "POLX", "pair" : "BTC_XRP", "ratio" : "10.33"}
{"exchange" : "POLX", "pair" : "BTC_ETH", "ratio" : "45.55"}
{"exchange" : "POLX", "pair" : "BTC_DASH", "ratio" : "1.62"}
{"exchange" : "POLX", "pair" : "BTC_ZEC", "ratio" : "2.57"}
{"exchange" : "POLX", "pair" : "BTC_XLM", "ratio" : "3.60"}
{"exchange" : "POLX", "pair" : "BTC_LTC", "ratio" : "13.40"}
{"exchange" : "POLX", "pair" : "BTC_LSK", "ratio" : "1.48"}
{"exchange" : "POLX", "pair" : "BTC_ETC", "ratio" : "21.45"}
POLX	- TOTAL BTC:	5446.70748592 (48.36 %)

</pre>



## Logic

Logic flow for determining when deposit is required is currently handled via a shell script. Eventaully this will implented in python, 
for now this shall suffice by plugging the required variables into `transfer_engine.py` from the cli or script.

Psuedocode:

mqtt get balance streams cex poloniex bittrex

for exchanges in poloniex cex bittrex:

    for currency in portfolio
         balance_pct = (currency_balance * price_of_btc)
         if balance_pct < hedge_allocation  (-/+ 10 % or so)
             deposit_required = True
         # discuss: do we check   surpluss?
         elif balance_pct > hedge_allocation (-/+ 10 % or so)
             if exchange = bittrex or poloniex:
              withdrawal_possible(required?) = True (?)

         if deposit_required:
             # im stoned. TODO: finish this         
       

## MqTT

To check our balances on poloniex, subscrib to pbal2:

sub -h 172.31.21.170 -t pbal2 p -C 1|jq


Likewise, cbal2 for cex and bbal2 for bittrex.
