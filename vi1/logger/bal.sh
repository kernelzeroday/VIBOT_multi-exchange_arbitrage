#!/bin/bash
# run balance calc in a loop in case of crash


case "$@" in
-k|--kill)

kill `cat pidfile`
;;
*)

while true;do
python3.6 ./BalanceCalc.py 2>/dev/null & echo $! > pidfile;wait
sleep 0.5
done

;;
esac
