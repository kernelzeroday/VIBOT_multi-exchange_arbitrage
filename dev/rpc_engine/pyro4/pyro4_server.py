import Pyro4


@Pyro4.expose
class GreetingMaker(object):
    def get_fortune(self, name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Behold the warranty -- the bold print giveth and the fine print taketh away.".format(name)


daemon = Pyro4.Daemon()                # make a Pyro daemon
# register the greeting maker as a Pyro object
uri = daemon.register(GreetingMaker)

# print the uri so we can use it in the client later
print("Ready. Object uri =", uri)
# start the event loop of the server to wait for calls
daemon.requestLoop()
