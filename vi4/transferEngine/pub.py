#!/usr/bin/env python3.6
from sys import exit
import paho.mqtt.client as mqtt
# Let's create a demonstration...

demo = True


# This is the Publisher
def mqPublish(msg):
    if demo:
        msg = str(msg)
        print("[*] Demo mode: request: \n %s" % msg)
        return
    client = mqtt.Client(client_id="publish_transfer", clean_session=False)
    client = mqtt.Client('tester')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("localhost", 1883, 60)
    client.publish("transfers/incoming", str(msg))
    client.disconnect()


currency = input('>> Currency: ')
amount = input('>> amount: ')
_from = input('>> From exchange: ')
to = input('>> To exchange: ')

proceed = input(
    'You requested a withdrawl of %s %s from %s to %s. Proceed? YES/NO : ' %
    (amount, currency, _from, to))
if proceed == 'YES':
    msg = (
        '\'{"action":"transfer","currency":"%s","amount":%s,"from":"%s","to":"%s"}\'' %
        (currency, amount, _from, to))
    mqPublish(msg)
