#!/usr/bin/env python3.6
import sys
import paho.mqtt.client as mqtt
import time
mq_subtop = 'verified'
debug = True
# This is the Subscriber


def timeStamp():
    return(str(time.time()))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mq_subtop)


def on_message(client, userdata, msg):
    if msg.payload.decode() == "quit":
        client.disconnect()
    else:
        message = (msg.payload.decode())
        t = timeStamp()
        if debug:
            print(message)
        with open('trades.log', 'a') as f:
            f.write(message + "\n")
        # client.disconnect()


def mqsub():

    client = mqtt.Client('log_py')
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
