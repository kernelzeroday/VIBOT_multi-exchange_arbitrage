/* Wrapper for connecting to mqtt easily */
package vilib

import (
	"fmt"
	"net"
	"os"

	proto "github.com/huin/mqtt"
	"github.com/jeffallen/mqtt"
)

type (
	MQTT struct {
		Host string // server:port
		Conn *mqtt.ClientConn
	}
)

func NewMQTT(host, client, user, pass string) *MQTT {
	conn, err := net.Dial("tcp", host)
	if err != nil {
		fmt.Fprint(os.Stderr, "dial: ", err)
		return nil
	}
	cc := mqtt.NewClientConn(conn)
	cc.ClientId = client
	if err := cc.Connect(user, pass); err != nil {
		fmt.Fprintf(os.Stderr, "connect: %v\n", err)
		return nil
	}
	return &MQTT{
		Host: host,
		Conn: cc,
	}
}

func (self *MQTT) Subscribe(topics ...string) {
	var tq []proto.TopicQos
	for _, v := range topics {
		tq = append(tq, proto.TopicQos{
			Topic: v,
			Qos:   proto.QosAtMostOnce,
		})
	}
	self.Conn.Subscribe(tq)
}

func (self *MQTT) Publish(topic string, message []byte) {
	self.Conn.Publish(&proto.Publish{
		TopicName: topic,
		Payload:   proto.BytesPayload(message),
	})
}
