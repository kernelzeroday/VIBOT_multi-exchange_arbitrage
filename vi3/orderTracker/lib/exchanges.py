import bittrexlib as Bittrex
import pololib as Poloniex
import cexlib as Cex



def Exchange(exchange,action,pair=None,price=0.0,amount=0.0):

    def ticker(exchange,pair):

        def poloniex_ticker(pair):
            ret = Poloniex.ticker(pair)

        def bittrex_ticker(pair):
            ret = Bittrex.ticker(pair)

        def cex_ticker(pair):
            ret = Cex.ticker(pair)

        if exchange == 'poloniex':
            ret = poloniex_ticker(pair)
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_ticker(pair)
            return ret
        elif exchange == 'cex':
            ret = cex_ticker(pair)
            return ret
        else:
            return('Invalid exchange')

    def balances(exchange):

        def poloniex_balances():
            ret = Poloniex.balances()
            return ret
        
        def bittrex_balances():
            ret = Bittrex.balances()
            return ret
        
        def cex_balances():
            ret = Cex.balances()
            return ret
        
        if exchange == 'poloniex':
            ret = poloniex_balances()
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_balances()
            return ret
        elif exchange == 'cex':
            ret = cex_balances()
            return ret
        else:
            return('Invalid exchange')



    def open_orders(exchange):

        def poloniex_orders():
            ret = Poloniex.orders()
            return ret

        def bittrex_orders():
            ret = Bittrex.orders
            return ret

        def cex_orders():
            ret = Cex.orders()
            return ret
        
        if exchange == 'poloniex':
            ret = poloniex_orders()
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_orders()
            return ret
        elif exchange == 'cex':
            ret = cex_orders()
            return ret
        else:
            return('Invalid exchange')


    def buy_limit(exchange,pair,amount,price):

        def poloniex_buy(pair,amount,price):
            ret = Poloniex.buy(pair,amount,price)
            return ret

        def bittrex_buy(pair,amount,price):
            ret = Bittrex.buy(pair,amount,price)
            return ret
        def cex_buy(pair,amount,price):
            ret = Cex.buy(pair,amount,price)
            return ret
        
        if exchange == 'poloniex':
            ret = poloniex_buy(pair,amount,price)
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_buy(pair,amount,price)
            return ret
        elif exchange == 'cex':
            ret = cex_buy(pair,amount,price)
            return ret
        else:
            return('Invalid exchange')


    def sell_limit(exchange,pair,amount,price):
        
        def poloniex_sell(pair,amount,price):
            ret = Poloniex.sell(pair,amount,price)
            return ret

        def bittrex_sell(pair,amount,price):
            ret = Bittrex.sell(pair,amount,price)
            return ret
        def cex_sell(pair,amount,price):
            ret = Cex.sell(pair,amount,price)
            return ret
        

        if exchange == 'poloniex':
            ret = poloniex_sell(pair,amount,price)
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_sell(pair,amount,price)
            return ret
        elif exchange == 'cex':
            ret = cex_sell(pair,amount,price)
            return ret
        else:
            return('Invalid exchange')


    def cancel_order(exchange,orderID):
        def poloniex_cancel(orderID):
            ret = Poloniex.cancel(orderID)
            return ret
        def bittrex_cancel(orderID):
            ret = Bittrex.cancel(orderID)
            return ret
        def cex_cancel(orderID):
            ret = Cex.cancel(orderID)
            return ret


        if exchange == 'poloniex':
            ret = poloniex_cancel(orderID)
            return ret
        elif exchange == 'bittrex':
            ret = bittrex_cancel(orderID)
            return ret
        elif exchange == 'cex':
            ret = bittrex_cancel(orderID)
            return ret
        else:
            return('Invalid exchange')





    if action == 'ticker':
        ret = ticker(exchange,pair)
        return ret
    elif action == 'balances':
        ret = balances(exchange)
        return ret
    elif action == 'orders':
        ret = open_orders(exchange)
        return ret
    elif action == 'buy':
        ret = buy_limit(exchange,pair,amount,price)
        return ret
    elif action == 'sell':
        ret = sell_limit(exchange,pair,amount,price)
        return ret
    elif action == 'cancel':
        ret = cancel_order(exchange,orderID)
    else:
        return("Invalid action")

