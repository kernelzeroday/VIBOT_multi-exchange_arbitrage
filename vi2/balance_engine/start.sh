#!/bin/bash

bInit(){
while true; do
echo 'Starting bittrex balance stream.'
./bBal.py
wait
done
}

pInit(){
echo 'Starting poloniex balance stream'
while true; do
./pBal.py
wait
done
}

cInit(){
echo 'Starting cex balnce stream'
while true;do
./cBal.py
wait
done
}

binInit(){
echo 'Starting binance balance stream'
while true;do
./binBal.py
wait
done
}


oInit(){
echo 'Starting poloniex balance stream'
while true;do
./okbal.py
wait
done

}

main(){
bInit &
pInit &
cInit &
binInit &
oInit &
}

echo 'Starting streams...'
main >> eng.log
