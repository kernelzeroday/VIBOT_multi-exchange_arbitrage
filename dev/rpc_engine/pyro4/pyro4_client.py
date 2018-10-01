# saved as greeting-client.py
import Pyro4

uri = input("What is the Pyro uri of the greeting object? ").strip()
name = input("What is your name? ").strip()

# get a Pyro proxy to the greeting object
greeting_maker = Pyro4.Proxy(uri)
print(greeting_maker.get_fortune(name))   # call method normally
