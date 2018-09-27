from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from threading import Thread
import asyncio

@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]

@dispatcher.add_method
def setflag(**kwargs):
  if kwargs is not None:
    for key, value in kwargs.items():
      print ("{0} == {1}".format(key,value))


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')

async def run():
    run_simple('localhost', 4000, application)

def start_loop():
  loop.run_until_complete(run())

loop = asyncio.get_event_loop()
t = Thread(target=start_loop)
t.start()


print("Work done outside of loop")
