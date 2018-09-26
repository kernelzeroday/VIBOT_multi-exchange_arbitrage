#!/bin/bash
# cex/polotool balance call wrapper

echo 'Poloniex BTC / ZEC / XRP / ETH / DASH / XLM  /LTC / LSK / XMR / ETC balances:'
./polotool -B| jq ".exchange.BTC,.exchange.ZEC,.exchange.XRP,.exchange.ETH,.exchange.DASH,.exchange.STR,.exchange.LTC,.exchange.LSK,.exchange.XMR,.exchange.ETC"
echo 'Cexio BTC/ ZEC / XRP  / ETH / DASH / XLM balances:'
./cextool -B| jq ".BTC.available,.ZEC.available,.XRP.available,.ETH.available,.DASH.available,.XLM.available"
echo 'Bittrex Balances:'
./bittrextool -B|jq ".[0].Currency,.[0].Balance,.[1].Currency,.[1].Balance,.[2].Currency,.[2].Balance,.[3].Currency,.[3].Balance,.[4].Currency,.[4].Balance,.[5].Currency,.[5].Balance,.[6].Currency,.[6].Balance,.[7].Currency,.[7].Balance,.[8].Currency,.[8].Balance,.[9].Currency,.[9].Balance,.[10].Currency,.[10].Balance,.[11].Currency,.[11].Balance"
#| tr "\n" ' : '
echo
