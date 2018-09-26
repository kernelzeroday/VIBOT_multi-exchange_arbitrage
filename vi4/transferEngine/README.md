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

action: transfer , Currency: XEM, Amount: 130000, From: bittrex, To: poloniex                                                                                                   [56/1963]
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


Interactive mode:

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
