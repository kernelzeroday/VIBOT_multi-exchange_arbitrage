import os
import json
import subprocess
from utils.helpers import get_config, list_to_string
from arbitrage_interface.settings import SCRAPPER_PATH, TRADE_ENGINE_PATH, BALANCE_ENGINE_PATH, ORDER_TRACKING_ENGINE_PATH, TRANSFER_ENGINE_PATH, LOG_ENGINE_PATH



def exec(*command, stdout_on=False, cwd=None):
    if stdout_on:
        return subprocess.check_output(command).decode('utf-8')
    else:
        if cwd:
            subprocess.Popen(command, cwd=cwd)
        else:
            subprocess.Popen(command)


def start_handler():
    _disable_engine()
    config = get_config()
    path = SCRAPPER_PATH
    try:
        cmd = "./scraper -currency '%s' -exchanges %s" % (list_to_string(config['pairs']), list_to_string(config['exchanges']))
        exec('cd /', '&&', 'cd %s' % path, '&&', cmd)
        pids = list(filter(
            None, exec('sudo', 'pgrep', '-f', 'scraper.go', stdout_on=True)
                .split('\n')))
        assert pids
        with open(os.getcwd() + 'arb_config.json', 'wb') as pid_file:
            pid_file.write("\n".join(pids))
        return {'success':True, 'text':'Vibot started pid: %s' % pids}
    except Exception as e:
        #todo: add log here
        return {'success':False, 'error':str(e)}
    # # run trade engine
    # path = TRADE_ENGINE_PATH
    # cmd = "./trade_current.py"
    # # run balance engine
    # path = BALANCE_ENGINE_PATH
    # cmd = "./start.sh"
    # # run order tracking engine
    # path = ORDER_TRACKING_ENGINE_PATH
    # cmd = "/OrderTrack.py"
    # # run transfer engine
    # path = TRANSFER_ENGINE_PATH
    # cmd = "./start.sh"
    # # run log engine
    # path = LOG_ENGINE_PATH
    # cmd = "./log.py"


def _disable_engine():
    with open(os.getcwd() + 'arb_config.json', 'r') as pid_file:
        pids = pid_file.read()
    for pid in pids:
        exec('sudo', 'kill', '-SIGKILL', pid)

def stop_handler():
    print('stop_handler')
    try:
        _disable_engine()
    except Exception as e:
        #todo: add log here
        return {'success':False, 'error':str(e)}

def pause_handler():
    print('pause_handler')
    return {'success': False, 'error': "Pause doesn't work. Under constracrion"}

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