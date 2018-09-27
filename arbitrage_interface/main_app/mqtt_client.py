import json
from arbitrage_interface.settings import MQ_HOST, MQ_PORT, MQ_KEEP_ALIVE, MQ_USER, MQ_PASSWORD, MQ_BIND_ADDRESS, MQ_SUBTOP
from utils.helpers import DecimalEncoder
import paho.mqtt.client as mqtt


CLIENTS = {}




# MQTT FUNCTIONS
def getTopicFunc(topic): ## why?
    """ This function maps incoming mq topics to a parsing function
    :param topic:   MQTT Subscription Topic
    :return         function to handle MQTT message body, or False
    """
    global EXCHANGES
    funcMap = {
        "bbal2": EXCHANGES["bittrex"].updateBalance if "bittrex" in EXCHANGES else False,
        "cbal2": EXCHANGES["cex"].updateBalance if "cex" in EXCHANGES else False,
        "pbal2": EXCHANGES["poloniex"].updateBalance if "poloniex" in EXCHANGES else False,
    }
    return funcMap.get(topic, False)

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
    """
    if "/engine_manager" in message.topic:
        #todo: handle answer here
        pass


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
        print("Connected Successfully")
    else:
        print("Refused %s" % rc)


def mqDisconnect(client, userdata, rc):
    """ MQTT Connect Event Listener
    :param client:      Client instance
    :param userdata:    Private userdata as set in Client() or userdata_set()
    :param rc:          Int of disconnection state:
                            0: Expected Disconnect IE: We called .disconnect()
                            _: Unexpected Disconnect
    """
    if rc == 0:
        print("Disconnected")
    else:
        print("Error: Unexpected Disconnection")


def mqPublish(id, payload, topic='engine_manager', qos=0, retain=False):
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
    client = CLIENTS.get(id, False)
    if not client:
        raise ValueError("Could not find an MQTT Client matching %s" % id)
    client.publish(topic, payload=payload, qos=qos, retain=retain)
    print('seems like success publish')


def mqStart(streamId):
    """ Helper function to create a client, connect, and add to the Clients recordset
    :param streamID:    MQTT Client ID
    :returns mqtt client instance
    """
    global CLIENTS
    client = mqtt.Client(streamId, clean_session=False)
    client.username_pw_set(MQ_USER, MQ_PASSWORD)
    # Event Handlers
    client.on_connect = mqConnect
    client.on_disconnect = mqDisconnect
    client.on_message = mqParse
    # Client.message_callback_add(sub, callback) TODO Do we want individual handlers?
    # Connect to Broker
    client.connect(MQ_HOST, port=MQ_PORT,
                   keepalive=MQ_KEEP_ALIVE, bind_address=MQ_BIND_ADDRESS)
    # # Subscribe to Topics
    # client.subscribe(SUBSCRIPTIONS)  # TODO Discuss QoS States
    client.loop_start()
    CLIENTS[streamId] = client
    return client


# MAIN
def main():
    global CLIENTS
    # Start a MQ Client
    client = mqStart(MQ_SUBTOP)




if __name__ == "__main__":
    main()
    #mq_publish example
    msg = json.dumps({"method": "setflag","params": {"key":"lmao","value":"lol"},"jsonrpc": "2.0","id": 0},cls=DecimalEncoder)
    mqPublish(MQ_SUBTOP, msg, topic=MQ_SUBTOP)
