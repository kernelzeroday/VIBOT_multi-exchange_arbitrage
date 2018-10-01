from jsonrpc2_zeromq import RPCClient

c = RPCClient("tcp://127.0.0.1:57570")
print(c.echo("Echo?"))

# Assuming the above compliant server, should print "Echo?"
