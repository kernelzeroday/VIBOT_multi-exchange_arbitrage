#!/bin/bash
# Hacky Wrapper for poloniex balance stream
# Kaito we need a damn api key for vi2!
pidfile='pbal.pid'

start(){

echo -ne 'Starting poloniex balanace stream...\nPress cntrl+c to quit'

while true ; do
python3.6 ./pBal.py >pbal.log 2>&1
done


}

start
