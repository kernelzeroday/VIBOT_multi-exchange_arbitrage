import os
import json
import subprocess
from utils.helpers import get_config, get_pids, set_pids, list_to_string, params_to_flags
from config import CMD_MAP


def exec(*command, stdout_on=False, cwd=None):
    if stdout_on:
        return subprocess.check_output(command).decode('utf-8')
    else:
        if cwd:
            subprocess.Popen(command, cwd=cwd)
        else:
            subprocess.Popen(command)


def start_handler(engine, params, first_disable=True):
    if first_disable:
        _disable_engine(engine)
    path, run_cmd = CMD_MAP[engine]['path'], CMD_MAP[engine]['run_cmd']
    flags = params_to_flags(params)
    try:
        exec('cd ..', '&&', 'cd %s' % path, '&&', run_cmd, flags)
        pids = list(filter(
            None, exec('sudo', 'pgrep', '-f', 'scraper.go', stdout_on=True)
            .split('\n')))
        assert pids
        set_pids(engine, pids)
        return {'success': True, 'text': 'Vibot started pid: %s' % pids}
    except Exception as e:
        # todo: add log here
        return {'success': False, 'error': str(e)}


def _disable_engine(engine):
    try:
        pids = get_pids(engine)
        for pid in pids:
            exec('sudo', 'kill', '-SIGKILL', pid)
    except Exception as e:
        msg = 'Cancelation %s engine error: %s' % (engine, str(e))
        print(msg)
        # todo: add log here


def stop_handler(engine):
    print('stop_handler')
    try:
        _disable_engine(engine)
    except Exception as e:
        # todo: add log here
        return {'success': False, 'error': str(e)}


def pause_handler(state, params=None):
    engine = 'scraper'
    try:
        if state == "pause":
            _disable_engine(engine)
        elif state == 'unpause':
            start_handler(engine, params, first_disable=False)
        return {'success': True, 'text': 'Successful %s' % state}
    except Exception as e:
        # todo: add log here
        raise Exception('Cancelation %s engine error: %s' % (engine, str(e)))


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
