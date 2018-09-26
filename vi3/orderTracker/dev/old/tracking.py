#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
print('[*] Starting Order Tracking Engine...')
mq_pubtop='Tracking'
import time,os,sys,json,threading,logging,signal,random
import paho.mqtt.client as mqtt
import config
import bittrex
import poloniex
import cexio
from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle
from exchanges import Exchange
# vars
verbose=True
debug=True
simulate=False
mq_on=True
count=0
retry=0
maxThreads = 10000
# logger stuff
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('orderTracking.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# singal handler for ctl+c
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# json hack (not currently used)
class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_python_object': b64encode(pickle.dumps(obj)).decode('utf-8')}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(b64decode(dct['_python_object'].encode('utf-8')))
    return dct
# return unix time
def tS():
    return time.time()
# print to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_ticker(exchange,pair,mode):
    def bittrex_ticker(pair,mode):
        bittrexAPI = bittrex.bittrex(config.bittrexKey, config.bittrexSecret)
        pair = str(pair)
        if pair == 'null':
            eprint('WARN: No pair specified, defaulting to BTC-ETH')
            pair == 'BTC-ETH'
        try:
            t = bittrexAPI.getticker(pair)
        except Exception as err:
            logger.error(err)
            eprint('Error getting ticker data: '+str(err))
            return False
        else:
            tt = json.dumps(t)
            tt = json.loads(tt)
            if mode == 'buy':
                tt = tt['Ask']
            elif mode == 'sell':
                tt = tt['Bid']
            return(tt)

    def polo_ticker(pair,mode):
        data = poloniex.Poloniex(config.poloniexKey,config.poloniexSecret)
        ticker = data.returnTicker()
        # this fixes json!
        ret = json.dumps(ticker[pair],cls=PythonObjectEncoder)
        ret = json.loads(ret,object_hook=as_python_object)
        if mode == 'buy':
            ret = ret['lowestAsk']
        elif mode == 'sell':
            ret = ret['highestBid']
        logger.info("Ticker call: "+str(ret))
        return(ret)
    
    def cex_ticker(pair,mode):
        try:
            pair = str(pair)
            api = cexio.Api(config.cexUser, config.cexKey, config.cexSecret)
            data = json.dumps(api.ticker(pair))
            data = json.loads(data)
            if mode == 'buy':
                data = data['ask']
            elif mode == 'sell':
                data = data['bid']
            return(data)
        except Exception as err:
            print("Error: %s" % err)
            return False
    
    if exchange == 'poloniex':
        ticker = polo_ticker(pair,mode)
    elif exchange == 'cex':
        ticker = cex_ticker(pair,mode)
    elif exchange == 'bittrex':
        ticker = bittrex_ticker(pair,mode)
    else:
        return('Invalid Exchange')
    if debug:print('[i] Ticker call...' + str(ticker))
    if ticker: return(ticker)


# main cancel order function
def cancel_order(exchange,orderID):
    logger.info('Cancel order: %s on %s' %(orderID,exchange))
    # sub functions for each exchange
    def cancel_bittrex(order_id):
        bittrexAPI = bittrex.bittrex(config.bittrexKey, config.bittrexSecret)
        try:
            ret = bittrexAPI.cancel(order_id)
        except Exception as err:
            logger.info("Error canceling bittrex error" + str(err))
            return False
        else:
            if ret == '':
                logger.info("Successfully canceled bittrex order")
                mqPublish('[*] Successfully canceled order %s' % order_id)
                return True
            else:
                if debug: print("[!] Failed cancel bittrex order call: "+str(ret))
                return False


    def cancel_poloniex(order_id):
        poloniexAPI = poloniex.Poloniex(config.poloniexKey,config.poloniexSecret)
        try:
            ret = poloniexAPI.cancelOrder(order_id)
        except Exception as err:
            logger.info("Error canceling poloniex order " + str(err))
            return False
        else:
            #ret = json.dumps(ret)
            logger.info("Successfully cancled poloniex order")
            mqPublish("[*] Successfully cancled poloniex order")
            #if debug: print("[*] Cancel poloniex order call: " + str(ret))
            return True

    def cancel_cex(order_id):
        cexioAPI = cexio.Api(config.cexUser, config.cexKey, config.cexSecret)
        try:
            ret = cexioAPI.cancel_order(str(order_id))
        except Exception as err:
            logger.info("Error canceling cex order " + str(err))
            return False
        else:
            #ret = json.dumps(ret)
            logger.info("Successfully canceled cex order" +str(ret))
            #if debug: print("[*] Cancel cex order call: "+str(ret))
            mqPublish("[*] Successfully canceled cex order: "+str(ret))
            return True
    # simulation mode
    if simulate:
        print("[*] (simulation) Canceling order: %s on exchange: %s" % (orderID,exchange))
        return True
    else:
        # live mode
        if exchange == 'bittrex':
            ret = cancel_bittrex(orderID)
            if ret: return True
        if exchange == 'poloniex':
            ret = cancel_poloniex(orderID)
            if ret: return True
        if exchange == 'cex':
            ret = cancel_cex(orderID)
            if ret: return True
    mqPublish("[*]" +str(ret))

def viable(mode,orig,new,c=0):
    #def retry(retry):
    #    retry+=1
    #    return int(retry)
    if debug: print("[i] DEBUG: " +str(mode) + " " + str(orig)+ " " +str(new))
    #count+=1
    #print("[i] Attempts: " +str(c))
    #if count == 3: return False
    if mode == 'sell':
        decrease = float(orig) - float(new)
        pct = float(decrease) / float(orig) * float(100.00)
        if float(pct) <= 0.25 and float(pct) > 0.0 :
           if debug: print('[i] : Viable:' + str(pct))
           return True
        else:
           if debug:print("[i] Pct was: " +str(pct))
           return False
    elif mode == 'buy':
        increase = float(new) - float(orig)
        pct = float(increase) / float(orig) * float(100)
        if float(pct) <= 0.2 and float(pct) =< -0.1:
            if debug: print('[i] : Viable: ' + str(pct))
            return True
        else:
            if debug:print("[i] Pct was: " +str(pct))
            return False
    else:
       logger.info('Error: Invalid mode.')
       return False
    #if debug:print("Pct was: " +str(pct))

# que order, check until expired using entropy to throw off analysis
def que_Order(exchange,expire,orderID,type_,price,pair,qty):
    t = random.randint(5,30)
    vt = random.randint(30,90)
    svt = random.randint(30,90)
    ok=False
    mode = str(type_)
    while True:
        if float(expire) <= tS():
            current = get_ticker(exchange,pair,mode)
            if mode == 'sell':
                if viable(mode,price,current):
                    mqPublish('[*] Sell Order still viable, not canceling for: %.8f seconds!' % svt)
                    logger.info('Sleeping for %.8f seconds' % svt)
                    time.sleep(svt)
                else:
                    mqPublish('[*] Sell %s order timed out, canceling...' % exchange)
                    logger.info('%s Sell order timed out, canceling...' % exchange)
                    if not ok:
                        ret = cancel_order(exchange,orderID)
                        ok=True
                    time.sleep(30)
                    current = get_ticker(exchange,pair,mode)
                    if float(price) <= float(current):
                        ret = Exchange(exchange,mode,pair,price,qty)
                        
                        mqPublish('[*] Sell order placed! %s %s %s %s '% (exchange,pair,price,qty))
                        break
                    else:
                        mqPublish("[*] Sleeping for 30 seconds, order still not viable.")

            elif mode == 'buy':
                if viable(mode,price,current):
                    mqPublish('[*] Buy Order still viable, not canceling for: %.8f seconds!' % vt)
                    logger.info('Sleeping for %.8f seconds' % vt)
                    time.sleep(vt)
                else:
                    mqPublish('[*] Buy %s order timed out, canceling...' % exchange)
                    logger.info('%s Buy order timed out, canceling...' % exchange)
                    #ret = cancel_order(exchange,orderID)
                    if not ok:
                        ret = cancel_order(exchange,orderID)
                        ok=True
                    time.sleep(30)
                    current = get_ticker(exchange,pair,mode)
                    if float(price) >= float(current):
                        ret = Exchange(exchange,mode,pair,price,qty)
                        
                        mqPublish('[*] Buy order placed! %s %s %s %s '% (exchange,pair,price,qty))
                        break
                    else:
                           mqPublish("[*] Sleeping for 30, order still not viable.")
                    
        else:
            time.sleep(t)



# connect to MqTT Stream
def mqConnect(client, userdata, flags, rc):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param flags:       Dict of broker reponse flags
    :param rc:          Int of connection state from 0-255:
                            0: Successful
                            1: Refused: Incorrect Protocol
                            2: Refused: Invalid Client ID
                            3: Refused: Server Unavailable
                            4: Refused: Incorrect User/Password
                            5: Refused: Not Authorised
    """
    if rc == 0:
        print("[*] Connected Successfully")
    else:
        print("[!] Refused %s" % rc)

# Disconnect from mqtt
def mqDisconnect(client, userdata, rc):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param rc:          Int of disconnection state:
                            0: Expected Disconnect IE: We called .disconnect()
                            _: Unexpected Disconnect
    """
    if rc == 0:
        print("[*] Disconnected")
    else:
        print("[!] Error: Unexpected Disconnection")

# On message function. Main logic here
def mqParse(client, userdata, message):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param message:     Dict of message details: {
                            topic:      String of the message topic
                            payload:    Bytes of the message body
                            qos:        Int of QoS state:
                                            0: Sent once without confirmation
                                            1: Sent at least once with confirmation required
                                            2: Sent exactly once with 4-step handshake.
                            retain:     Bool of Retain state
                        }

    {
      "Exchange": "bittrex",
      "Pair": "BTC-XLM",
      "Kind": "Limit",
      "Type": "sell",
      "OrderID": "793fc1d6-c8cf-42e3-b134-6a4a93326e18",
      "Price": "0.00003897",
      "Qty": "596",
      "Timestamp": 1519088368.0660238,
      "Expires": 1519088668.0660238
    }

   """
    # Load the json object
    #if debug: print(str(message.payload))
    try:
        obj = json.loads(str(message.payload.decode('UTF-8')))
    except Exception as err:
        eprint('ERROR: %s error loading json!' % err)
        bad_data=True
    else:
        bad_data=False
        #if debug: print(obj)
    # Parse the object
    if not bad_data:
        try:
            exchange = obj['Exchange']
        except Exception as err:
            eprint('Error parsing Exchange from object: ' + str(err))
            return False
        try:
            orderID = obj['OrderID']
        except:
            eprint('Error parsing OrderID from object')
            return False
        try:
            kind = obj['Kind']
        except:
            eprint('Error parsing Kind from object')
            return False
        try:
            expires = obj['Expires']
        except:
            eprint('Error parsing Expires from object')
            return False
        try:
            price = obj['Price']
        except:
            eprint('Error parsing Price from object')
            return False
        try:
            _type = obj['Type']
        except:
            eprint('Error parsing Type from object')
            return False
        try:
            pair = obj['Pair']
        except:
            eprint('Error parsing Pair from object')
            return False
        try:
            qty = obj['Qty']
        except:
            eprint('Error parsing Qty from object')
            return False
            
    # declare as string variables
    try:
        kind_ = str(kind)
        orderID_ = str(orderID)
        exchange_ = str(exchange)
        expires_ = str(expires)
        price_ = str(price)
        _type_ = str(_type)
        pair_ = str(pair)
        qty_ = str(qty)
    except Exception as err:
        print(err)
    # Received an order, prepare to que
    if kind_ == 'Limit':
        if verbose or debug or mq_on:
            mqPublish("[*] Tracking new order on exchange %s : %s , expires %s " % (exchange_,orderID_,expires_))
        with open('pending.log', 'a') as f:
            f.write("""'{"OrderID":%s,"Type":%s,"Price":%s}'\n""" % (orderID,_type,pair_))
        threads=[]
        count=0

        #TODO: thread tracking
        
        if count>int(maxThreads):
            print("[*] Stopping because reached max threads (%s)" % maxThreads)
            logger.info('Too many threads open!')
            return
        else:
            t = threading.Thread(target=que_Order, args=(exchange_,expires_,orderID_,_type_,price_,pair_,qty_ ))
            t.start()
            count+=1
        if count % 10 == 0:
            activeThreads = (threading.active_count())
            print("[*] Processed %s orders" % activeThreads)

    if kind == 'Limit':
        mqPublish('[*] Order %s on exchange %s qued in thread for tracking' % (orderID_,exchange_))
        logger.info('Order %s on exchange %s qued in thread for tracking' % (orderID_,exchange_))




#TODO: Publish Canceled Order Info to stream ('canceled')?
def mqPublish(payload, topic=mq_pubtop, qos=0, retain=False):
    """ MQTT Publish Message to a Topic
    :param id           String of the Client ID
    :param topic:       String of the message topic
    :param payload:     String of the message body
    :param qos:         Int of QoS state:
                            0: Sent once without confirmation
                            1: Sent at least once with confirmation required
                            2: Sent exactly once with 4-step handshake.
    :param retain:      Bool of Retain state
    :return             Tuple (result, mid)
                            result: MQTT_ERR_SUCCESS or MQTT_ERR_NO_CONN
                            mid:    Message ID for Publish Request
    """
    global CLIENTS
    client = mqtt.Client('trackpub', clean_session=False)
    if not client:
        raise ValueError("Could not find an MQTT Client matching %s" % id)
    if debug:print(payload)
    client.publish('tracking', payload=payload, qos=qos, retain=retain)


def mqStart(streamId):
    """ Helper function to create a client, connect, and add to the Clients recordset
    :param streamID:    MQTT Client ID
    :returns mqtt client instance
    """
    global CLIENTS
    client = mqtt.Client(streamId, clean_session=False)
    client.username_pw_set(config.mq_user, config.mq_pass)
    # Event Handlers
    client.on_connect = mqConnect
    client.on_disconnect = mqDisconnect
    client.on_message = mqParse
    # Client.message_callback_add(sub, callback) TODO Do we want individual handlers?
    # Connect to Broker
    client.connect(config.mq_host, port=config.mq_port,
                   keepalive=config.mq_keepalive, bind_address=config.mq_bindAddress)
    # Subscribe to Topics
    client.subscribe("verified")  # TODO Discuss QoS States
    client.loop_start()
    return client


client = mqStart("verified")
#mq_pubtop='tracking'
# just loop some sh*t to keep this open on the CLI
while 1:
    try:
        time.sleep(0.25)
    except KeyboardInterrupt:
        print('[*] Caught Signal, exiting gracefully.\nBye!')
        sys.exit(0)


