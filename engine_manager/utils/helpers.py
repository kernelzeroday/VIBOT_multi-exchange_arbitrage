import os
import json
from decimal import Decimal
from config import PID_FILE

def get_config():
    with open(os.getcwd() + '/arb_config.json', 'r') as config_file:
        return json.loads(config_file.read())
    # todo: add exception with logs


def list_to_string(pairs, separator=" "):
    return separator.join(pairs)


def params_to_flags(params):
    result = ""
    for key, value in params.items():
        if value != str:
            raise Exception('Unexpected params: %s' % params)
        if key == "pairs":
            value = list_to_string(value)
        #todo: add any custom flag handle here
        result+="".join([" ", "-", key, " ", "'", value, "'"])
    return result


def get_pids(engine):
    with open(PID_FILE, 'r') as data_file:
        config = json.load(data_file)
    return config


def set_pids(engine, pids):
    try:
        config = get_pids(engine)
        config[engine] = get_pids(engine)
        with open(PID_FILE, 'wb') as data_file:
            data_file.write(json.dumps(config))
    except Exception as e:
        raise Exception(('Unsuccess update of pids file %s: for updade engine: %s, pids: %s. Error: %s' % (PID_FILE, engine, pids, str(e))))



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

