import os
import json
import subprocess
from utils.helpers import get_config, list_to_string, DecimalEncoder
from .mqtt_client import MMQTClient
# from arbitrage_interface.settings import SCRAPPER_PATH, TRADE_ENGINE_PATH, BALANCE_ENGINE_PATH, ORDER_TRACKING_ENGINE_PATH, TRANSFER_ENGINE_PATH, LOG_ENGINE_PATH
from arbitrage_interface.settings import MQ_SUBTOP


def exec(*command, stdout_on=False, cwd=None):
    if stdout_on:
        return subprocess.check_output(command).decode('utf-8')
    else:
        if cwd:
            subprocess.Popen(command, cwd=cwd)
        else:
            subprocess.Popen(command)


def start_handler():
    msg = json.dumps({"method": "start_all_engines", "params": {
                     "key": "lmao", "value": "lol"}, "jsonrpc": "2.0", "id": 0}, cls=DecimalEncoder)
    MMQTClient().mqPublish(MQ_SUBTOP, msg, topic=MQ_SUBTOP)


def stop_handler():
    msg = json.dumps({"method": "stop_all_engines", "params": {
        "key": "lmao", "value": "lol"}, "jsonrpc": "2.0", "id": 0}, cls=DecimalEncoder)
    MMQTClient().mqPublish(MQ_SUBTOP, msg, topic=MQ_SUBTOP)


def pause_handler(state):
    if state == 'pause':
        method = 'pause'
    elif state == 'unpause':
        method = 'unpause'
    msg = json.dumps({"method": method,
                      "params": {"key": "lmao",
                                 "value": "lol"},
                      "jsonrpc": "2.0",
                      "id": 0},
                     cls=DecimalEncoder)
    MMQTClient().mqPublish(MQ_SUBTOP, msg, topic=MQ_SUBTOP)


def update_config_handler(data):
    print('update_config: %s' % (data))
    new_config = {}
    try:
        new_config['exchanges'] = data['exchanges']
        new_config['ARBITRAGE_CONFIG']['pairs'] = data['pairs']
        new_config['ARBITRAGE_CONFIG']['min_threshold'] = data['min_threshold']
        with open(os.getcwd() + 'arb_config.json', 'wb') as config_file:
            config_file.write(json.dumps(new_config))
    except Exception as e:
        return 'Unexpected config data: %s \n error: %s' % (new_config, str(e))
