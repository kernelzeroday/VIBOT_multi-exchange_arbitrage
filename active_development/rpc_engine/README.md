Possible candidates for RPC control:

xmlrpc  --  native xml python rpc implementation
PROS: native, highly configurable
CONS: xml, perhaps too complex for our purposes







PyRO4  --  python remote objects system
PROS: high configurability, ease of use
CONS: python only, no cross language use
EXAMPLE

Server:
$ python3 pyro4_server.py Ready. Object uri = PYRO:obj_e7edbe4595854c5e8d895a6cdbc62d9d@localhost:45367


Client:
$ python3 pyro4_client.py What is the Pyro uri of the greeting object? PYRO:obj_e7edbe4595854c5e8d895a6cdbc62d9d@localhost:45367
What is your name? john
Hello, john. Here is your fortune message:
Behold the warranty -- the bold print giveth and the fine print taketh away.

NOTES:

Need to verify authentication processes





jsonrpc2_zeromq --  json rpc over zeromq
PROS: universal interop with excellent transport over zmq
CONS: tbd
