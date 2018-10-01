import paho.mqtt.client as mqtt
from jsonrpc import JSONRPCResponseManager, dispatcher
from threading import Thread
import asyncio


@dispatcher.add_method
def setflag(**kwargs):
    if kwargs is not None:
        for key, value in kwargs.items():
            print("{0} == {1}".format(key, value))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/jsonrpc/request/#")


def on_message(client, userdata, msg):
    print("REQUEST: " + msg.payload.decode("utf-8"))
    response = JSONRPCResponseManager.handle(
        msg.payload.decode("utf-8"), dispatcher)
    print("RESPONSE: " + response.json)


async def run():
    client.loop_forever()


def start_loop():
    loop.run_until_complete(run())


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)


loop = asyncio.get_event_loop()
t = Thread(target=start_loop)
t.start()
