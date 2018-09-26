class ticker(object):
    """Object to hold a ticker on an exchange:

    Attributes:
        name: A string representing the ticker name. (cex_BTC_ETH)
        price: A float tracking the current price of the asset on the exchange.
    """

    def __init__(self, name, bid=0.0,ask=0.0):
        """Return a ticker object whose name is *name* and starting
        bid and ask are 0.0."""
        self.name = name
        self.bid = bid
        self.ask = ask

    def update(self, bid=0.0, ask=0.0):
        """Return the balance remaining after withdrawing *amount*
        dollars."""
        #if amount > self.balance:
        #    raise RuntimeError('Amount greater than available balance.')
        self.ask == ask
        self.bid == bid
        return self.bid,self.ask

    def check(self, side):
        """Return the price."""
        if side == 'bid':
            return self.bid
        elif side == 'ask':
            return self.ask
