import os
import json
from decimal import Decimal


def get_config():
    with open(os.getcwd() + '/arb_config.json', 'r') as config_file:
        return json.loads(config_file.read())
    # todo: add exception with logs


def list_to_string(pairs, separator=" "):
    return separator.join(pairs)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
