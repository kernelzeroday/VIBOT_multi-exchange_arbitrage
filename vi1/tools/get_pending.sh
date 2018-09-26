#!/bin/bash
cx_pending=$(./cextool -B| jq -r ".BTC.orders,.ETH.orders,.DASH.orders,.ZEC.orders,.XRP.orders")
cx_coins='BTC ETH DASH ZEC XRP'

echo 'Cex Pending Balances : '
echo "$cx_coins : "
for coin in "$cx_pending"; do 
    echo "$coin"
done


polo_pending=$(./polotool -A |jq ".BTC.onOrders,.ETH.onOrders,.DASH.onOrders,.ZEC.onOrders,.XRP.onOrders")

echo 'Poloniex Pending Balances : '
echo "$cx_coins : "
for coin in "$polo_pending"; do
    echo "$coin"
done
