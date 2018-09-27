Possible candidates for RPC control:

xmlrpc  --  native xml python rpc implementation
PROS: native, highly configurable
CONS: xml, perhaps too complex for our purposes

PyRO4  --  python remote objects system
PROS: high configurability, ease of use
CONS: python only, no cross language use

jsonrpc2_zeromq --  json rpc over zeromq
PROS: universal interop with excellent transport over zmq
CONS: tbd