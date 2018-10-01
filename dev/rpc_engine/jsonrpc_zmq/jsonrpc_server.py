from jsonrpc2_zeromq import RPCServer


class EchoServer(RPCServer):

    def handle_echo_method(self, msg):
        return msg


s = EchoServer("tcp://127.0.0.1:57570")
s.run()
