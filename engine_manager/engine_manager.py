import asyncio
import paho.mqtt.client as mqtt
from jsonrpc import JSONRPCResponseManager, dispatcher
from threading import Thread
from config import MQ_USER, MQ_PASS
from handlers import start_handler, pause_handler, stop_handler


@dispatcher.add_method
def setflag(**kwargs):
  if kwargs is not None:
    for key, value in kwargs.items():
      print ("{0} == {1}".format(key,value))


@dispatcher.add_method
def run_engine(**kwargs):
    """
    expected kwargs: {"method": "run_engine", "engine": "engine name" "params": {"flag1": "value1", "flag2": "value2"}
    """
    # todo: check method
    start_handler(kwargs["engine"], kwargs['params'])


@dispatcher.add_method
def stop_engine(**kwargs):
    """
    expected kwargs: {"method": "stop_engine", "engine": "engine name" "params": {"flag1": "value1", "flag2": "value2"}
    """
    # todo: check method
    start_handler(kwargs["engine"], kwargs['params'])

@dispatcher.add_method
def pause(**kwargs):
    """
    expected kwargs: {"method": "pause", "params": {"flag1": "value1", "flag2": "value2"}
    params: scraper params
    """
    # todo: check method
    pause_handler('pause')

@dispatcher.add_method
def unpause(**kwargs):
    """
    expected kwargs: {"method": "pause", "params": {"flag1": "value1", "flag2": "value2"}
    params: scraper params
    """
    # todo: check method
    pause_handler('unpause', kwargs['params'])


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("engineManager")

def on_message(client, userdata, msg):
    print("REQUEST: "+msg.payload.decode("utf-8"))
    response = JSONRPCResponseManager.handle(msg.payload.decode("utf-8"), dispatcher)
    print("RESPONSE: "+response.json)


async def run():
    client.loop_forever()

def start_loop():
  loop.run_until_complete(run())

client = mqtt.Client()
client.username_pw_set(MQ_USER, MQ_PASS)

client.on_connect = on_connect
client.on_message = on_message

client.connect('mqtt.flespi.io',1883,60)



loop = asyncio.get_event_loop()
t = Thread(target=start_loop)
t.start()


