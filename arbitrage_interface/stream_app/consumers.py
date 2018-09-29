from arbitrage_interface.settings import CHANNEL_GROUP_NAME, MQ_HOST, MQ_PORT, MQ_KEEP_ALIVE, MQ_USER, MQ_PASSWORD, MQ_BIND_ADDRESS, MQ_SUBTOP
from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from .mqtt_client import MMQTClient
import paho.mqtt.client as mqtt


class WSStreamCunsomer(AsyncJsonWebsocketConsumer):
    ##### MMQT event to WSS

    async def connect(self):
        """
        Called when the user is handshaking.
        """
        # Accept the connection
        await self.accept()

    async def receive_json(self, content):
        """
        Called when we get a mmqt event. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # # Messages will have a "command" key we can switch on
        # command = content.get("command", None)
        try:
            await self.send_json(
                {
                    # "msg_type": MSG_TYPE_MESSAGE,
                    # "topic": content["topic"],
                    "message": content["message"],
                },
            )
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})


class MMQTStreamCunsomer(AsyncJsonWebsocketConsumer):   #todo: Sync
    async def connect(self):
        self.mqStart(MQ_SUBTOP)

    async def update(self, message):
        await self.channel_layer.group_send(
            CHANNEL_GROUP_NAME,
            {
                "type": "recieve.json",
                # "topic": topic,
                "message": message,
            }
        )

    def mqStart(self, streamId):
        """ Helper function to create a client, connect, and add to the Clients recordset
        :param streamID:    MQTT Client ID
        :returns mqtt client instance
        """
        client = mqtt.Client(streamId, clean_session=False)
        client.username_pw_set(MQ_USER, MQ_PASSWORD)
        # Event Handlers
        client.on_connect = self.mqConnect
        client.on_disconnect = self.mqDisconnect
        client.on_message = self.mqParse
        # Client.message_callback_add(sub, callback) TODO Do we want individual handlers?
        # Connect to Broker
        client.connect(MQ_HOST, port=MQ_PORT,
                       keepalive=MQ_KEEP_ALIVE, bind_address=MQ_BIND_ADDRESS)
        # # Subscribe to Topics
        # client.subscribe(SUBSCRIPTIONS)  # TODO Discuss QoS States
        client.loop_start()
        self.client = client
        return client


    def mqPublish(self, id, payload, topic='engine_manager', qos=0, retain=False):
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
        client = self.client.get(id, False)
        if not client:
            raise ValueError("Could not find an MQTT Client matching %s" % id)
        client.publish(topic, payload=payload, qos=qos, retain=retain)


    def mqDisconnect(self, client, userdata, rc):
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


    def mqConnect(self, client, userdata, flags, rc):
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

    def mqParse(self, client, userdata, message):
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
        self.update(message)





class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def __init__(self, code):
        super().__init__(code)
        self.code = code