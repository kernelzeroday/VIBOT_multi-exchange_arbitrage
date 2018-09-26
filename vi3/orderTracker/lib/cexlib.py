#!/usr/bin/env python3.6
import json
import cex as cexio
import config as conf

from sys import exit


def get_fee_info():
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    try:
        ret = json.dumps(api.get_myfee)
    except Exception as err:
       print('Error: '+ str(err))
    else:
       print(ret)

def get_deposit_addresses_(currency):
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    try:
        ret = api.get_deposit_addresses(currency)
    except Exception as err:
       print('Error: ' + str(err))
    else:
       #ret = json.loads(ret)
       print(ret)

def ticker(pair):
    try:
        pair = str(pair)
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
        data = json.dumps(api.ticker(pair))
        print(data)
    except Exception as err:
        print("Error: %s" % err)
        return False

def convert_price(amount,pair):
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    #amount = float(amount)
    #pair = str(pair)
    try:
        ret = api.convert(amount,pair)
    except Exception as err:
        print(err)
        return False
    else:
        return(ret)

def balances():
    try:
        #api = cexapi.API(conf.username, conf.api_key, conf.api_secret)
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
        try:
            bal = json.dumps(api.balance)
        except Exception as err:
            print(err)
            return False
        #print(bal)
        #bal = json.dumps(bal)
        return(bal)
    except Exception as err:
        print("Error: %s" % err)
        return False

def orders(pair=''):
    try:
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
        if pair == 'null':
            orders = api.open_orders('')
        else:
            orders = api.open_orders(pair)
    except Exception as err:
        print(err)
    else:
        orders = json.dumps(orders)
        return(orders)

def orderBook(pair):
    try:
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
        if pair == 'null':
            book = api.order_book('1', 'BTC/USD')
        else:
            book = order_book = api.order_book('1',pair)
    except Exception as err:
        print(err)
    else:
        book = json.dumps(book)
        return(book)
    
def cancel(order_id):
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    try:
        ret = api.cancel_order(str(order_id))
    except Exception as er:
        print(er)
        return False
    else:
        return("Success")

def price_stats(hours, limit, pair):
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    if valid_pair(pair):
        try:
            ret = json.dumps(api.price_stats(hours, limit, pair))
        except Exception as err:
            print(err)
            return False
        else:
            ret = json.loads(ret)
            plist = []         
            for i in ret:
                price = str(i['price'])
                timestamp = str(i['tmsp'])
                plist.append("Price: "+price+" Time: "+timestamp)
            return list(plist)

    
    else:
        print("Invalid Pair")
        return False

def get_trade_hist(since, pair):
    """
    since - return trades with tid >= since (optional parameter, 1000 or all existing (if less than 1000), elements are returned if omitted)
    """
    api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    if valid_pair(pair):
        try:
            #ret = json.dumps(api.trade_history(since, pair))
            ret = api.trade_history(since, pair)
        except Exception as err:
            print(err)
            return False
        else:
            return(ret)
    else:
        print("Invalid pair specified")
        return False
        



def valid_pair(pair):
    try:
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
        last = json.dumps(api.ticker(pair)['last'])
    except Exception as err:
        print("Valid pair: %s" %err)
        return False
    else:
        return True


def buy(pair, amount, price):
    pair = str(pair)
    debug = True
    try:
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    except Exception as err:
        print(err)
        return False
    else:
        if float(amount) > float(0):
            if float(price) and float(price) > float(0.0):
                if valid_pair(pair):
                    try:
                        
                        ret = api.buy_limit_order(amount, price, pair)
                        
                        #ret = api.sell_limit_order(amount, price, pair)
                    except Exception as err:
                        print(err)
                        return False
                    else:
                        ret = json.dumps(ret)
                        order_info = json.loads(ret)
                        if debug: print(ret)
                        try:
                            order_type = order_info['type']
                            order_id = order_info['id']
                            order_time = order_info['time']
                            order_price = order_info['price']
                            order_amount = order_info['amount']
                            order_pending = order_info['pending']
                            order_complete = order_info['complete']
                        except Exception as err:
                            print(err)
                            return False
                        else:
                            print("Sucess. Order ID: %s posted at %s  " % (order_id,order_time,))
                            print("Type: %s Amount: %s at %s Complete: %s Pending: %s" %(order_type,order_amount,order_price,order_complete,order_pending))
                            return order_id
                else:
                    print("Invalid pair, not executing")
                    return False
            else:
                print("Invalid price, not exectuting")
                return False
        else:
            print("Invalid amount, not executing")
            return False
def sell(pair, amount, price):
    pair = str(pair)
    debug = True
    try:
        api = cexio.Api(conf.username, conf.api_key, conf.api_secret)
    except Exception as err:
        print(err)
        return False
    else:
        if float(amount) > float(0):
            if float(price) and float(price) > float(0.0):
                if valid_pair(pair):
                    try:
                        
                        #ret = api.buy_limit_order(amount, price, pair)
                        
                        ret = api.sell_limit_order(amount, price, pair)
                    except Exception as err:
                        print(err)
                        return False
                    else:
                        ret = json.dumps(ret)
                        order_info = json.loads(ret)
                        if debug: print(ret)
                        try:
                            order_type = order_info['type']
                            order_id = order_info['id']
                            order_time = order_info['time']
                            order_price = order_info['price']
                            order_amount = order_info['amount']
                            order_pending = order_info['pending']
                            order_complete = order_info['complete']
                        except Exception as err:
                            print(err)
                            return False
                        else:
                            print("Sucess. Order ID: %s posted at %s  " % (order_id,order_time,))
                            print("Type: %s Amount: %s at %s Complete: %s Pending: %s" %(order_type,order_amount,order_price,order_complete,order_pending))
                            return order_id
                else:
                    print("Invalid pair, not executing")
                    return False
            else:
                print("Invalid price, not exectuting")
                return False
        else:
            print("Invalid amount, not executing")
            return False

