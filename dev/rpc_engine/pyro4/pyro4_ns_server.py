# saved as greeting-server.py
import Pyro4


@Pyro4.expose
class GreetingMaker(object):
    def get_fortune(self, name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Tomorrow's lucky number is 12345678.".format(name)


daemon = Pyro4.Daemon()                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
# register the greeting maker as a Pyro object
uri = daemon.register(GreetingMaker)
# register the object with a name in the name server
ns.register("example.greeting", uri)

print("Ready.")
# start the event loop of the server to wait for calls
daemon.requestLoop()
