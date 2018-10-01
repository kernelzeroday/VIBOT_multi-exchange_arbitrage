Documentation link:
https: // json - rpc.readthedocs.io / en / latest / quickstart.html


Quickstart
Installation
Requirements: Python 2.6, 2.7, Python 3.x >= 3.2 or PyPy
To install the latest released version of package:

pip install json - rpc
Integration
Package is transport agnostic, integration depends on you framework. As an example we have server with Werkzeug and client with requests.

Server

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher


@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
Client

import requests
import json


def main():
    url = "http://localhost:4000/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "echo",
        "params": ["echome!"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["result"] == "echome!"
    assert response["jsonrpc"]
    assert response["id"] == 0


if __name__ == "__main__":
    main()
Package ensures that request and response messages have correct format. Besides that it provides jsonrpc.manager.JSONRPCResponseManager which handles server common cases, such as incorrect message format or invalid method parameters. Futher topics describe how to add methods to manager, how to handle custom exceptions and optional Django integration.


Method dispatcher
Dispatcher is used to add methods(functions) to the server.

For usage examples see Dispatcher.add_method()


class jsonrpc.dispatcher.Dispatcher(prototype=None)[source]


Dictionary like object which maps method_name to method.

__init__(prototype=None)[source]
Build method dispatcher.

Parameters: prototype(object or dict, optional) – Initial method mapping.
Examples

Init object with method dictionary.

>> > Dispatcher({"sum": lambda a, b: a + b})
None
add_method(f, name=None)[source]
Add a method to the dispatcher.

Parameters:
f(callable) – Callable to be added.
name(str, optional) – Name to register(the default is function f name)
Notes

When used as a decorator keeps callable object unmodified.

Examples

Use as method

>> > d = Dispatcher()
>> > d.add_method(lambda a, b: a + b, name="sum")
<function __main__. < lambda>>
Or use as decorator

>> > d = Dispatcher()
>> > @d.add_method


def mymethod(*args, **kwargs):
        print(args, kwargs)


build_method_map(prototype, prefix='')[source]
Add prototype methods to the dispatcher.

Parameters:
prototype(object or dict) – Initial method mapping. If given prototype is a dictionary then all callable objects will be added to dispatcher. If given prototype is an object then all public methods will be used.
prefix(string, optional) – Prefix of methods
