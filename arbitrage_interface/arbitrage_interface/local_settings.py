import os
import json
from utils.helpers import get_config


DEFAULT_CONFIG = get_config()


ALLOWS_CONFIG_ELEMENTS = {
    'exchanges':['poloniex','okex','bitfinex','binance','bittrex','tidex','hitbtc','tidex','idex','bx.in.th'],
    'pairs':['BTCUSD','ETHBTC','LTCBTC','ZRXBTC','ADABTC','REMBTC','VIBBTC','LSKBTC','EOSBTC']
}


ENGINES_MAP = {
    'vi1':['scrapper', 'order_engine'],
    'vi2':['balance_engine',],
    'vi3':['order_tracking_engine',],
    'vi4':['transfer',]
}


MQ_HOST = 'mqtt.flespi.io'
MQ_PORT = 1883
MQ_KEEP_ALIVE = 60
MQ_BIND_ADDRESS = ""
MQ_USER = 'u8mqGooxldO264DN5tse2jIesV9PfJjxFvNbI0xR39HY3aBXsRZiYxmfhkSmT1Jp'
MQ_PASSWORD = None
MQ_SUBTOP = 'engineManager'