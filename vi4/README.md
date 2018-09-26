# Vi4

## Transfer Engine

The transfer engine listens via mqtt for incoming json requests and moves funds between exchanges when a request is received

### Usage:

Start the engine in mqtt daemon mode:

    cd transferEngine
    ./transfer_bin.py -l -m


### Notes:


This component is potentially going to be phased out and replaced by a rebalance engine that does not require the transfering of funds to operate.
