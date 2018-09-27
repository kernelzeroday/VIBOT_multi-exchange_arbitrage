import os
import logging
import datetime

logging.basicConfig(filename='data.log', level=logging.INFO)


def log_handler(msg, type='info', **log):
    log['timestamp'] = datetime.datetime.now().timestamp()
    log['msg'] = msg
    if type == 'warning':
        logging.warning(log)
    elif type == 'error':
        logging.error(log)
    #todo: add your log type here..
    else:
        logging.info(log)
    return log