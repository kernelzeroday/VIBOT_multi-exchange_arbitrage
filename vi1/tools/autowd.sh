#!/bin/bash


# variables

#hardcoded to btc
currency='BTC'

exchange="$1"
amount="$2"
address="$3"


case "$exchange" in
bittrex)
#  -R, --auto_withdraw   Automated withdrawal (specify currency <-c>, amount
#                        <-a>, and address <-A>)

./bittrextool -R -c "$currency" -a "$amount"  -A "$address"

;;

binance)


#  -R, --auto_withdraw   Automated withdrawal ((specify currency <-c>, amount
#                        <-a>, and address <-A>)

./bintool -R -c "$currency" -a "$amount"  -A "$address"

;;

poloniex)


#  -R, --auto_withdraw   Automated Withdrawal [specify wallet_address (-W) ,
#                        amount (-a), and currency (-X) ]

./polotool -R -X "$currency" -W "$address" -a "$amount"

;;

*)
echo 'Invalid or unsupported exchange.'
echo 'Supported exchanges: poloniex bittrex binance'
echo "USAGE: $0 <exchange> <amount> <address> "
exit 1

;;

esac
