#!/usr/bin/env python3
import sys
import paho.mqtt.client as mqtt

mq_subtop = 'topic/test'

# This is the Subscriber


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mq_subtop)


def on_message(client, userdata, msg):
    if msg.payload.decode() == "quit":
        client.disconnect()
    else:
        print(msg.payload.decode())
        # client.disconnect()


def mqsub():

    client = mqtt.Client('subtest')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect("127.0.0.1", 1883, 60)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Caught Signal, exiting...\nBye!")
        sys.exit(0)


mqsub()
