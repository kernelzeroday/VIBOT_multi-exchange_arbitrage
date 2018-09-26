package vilib

import (
	"fmt"
	"log"
	"net"
	"net/http"
	"time"
)

type (
	Broker struct {
		// Events are pushed to this channel by the main events-gathering routine
		Notifier chan Message
		// New client connections
		newClients chan chan Message
		// Closed client connections
		closingClients chan chan Message
		// Client connections registry
		clients map[chan Message]bool
	}
	Message struct {
		Event   string
		Message []byte
	}
)

// the amount of time to wait when pushing a message to a slow client or a client that closed after `range clients` started.
const patience time.Duration = time.Second * 1

var (
	// Net Client with short timeouts
	// Default http.Client does not have proper timeouts defined
	netTransport = &http.Transport{
		Dial: (&net.Dialer{
			Timeout: 3 * time.Second,
		}).Dial,
		TLSHandshakeTimeout: 3 * time.Second,
	}
	netClient = &http.Client{
		Timeout:   time.Second * 5,
		Transport: netTransport,
	}
	// SSE = NewServer()
)

func NewServer() (broker *Broker) {
	// Instantiate a broker
	broker = &Broker{
		Notifier:       make(chan Message, 1),
		newClients:     make(chan chan Message),
		closingClients: make(chan chan Message),
		clients:        make(map[chan Message]bool),
	}
	// Set it running - listening and broadcasting events
	go broker.listen()
	return broker
}

func (broker *Broker) listen() {
	for {
		select {
		case s := <-broker.newClients:
			// A new client has connected.
			// Register their message channel
			broker.clients[s] = true
			log.Printf("Client added. %d registered clients", len(broker.clients))
		case s := <-broker.closingClients:
			// A client has dettached and we want to
			// stop sending them messages.
			delete(broker.clients, s)
			log.Printf("Removed client. %d registered clients", len(broker.clients))
		case event := <-broker.Notifier:
			// We got a new event from the outside!
			// Send event to all connected clients
			for clientMessageChan, _ := range broker.clients {
				select {
				case clientMessageChan <- event:
				case <-time.After(patience):
					log.Print("Skipping client.")
				}
			}
		}
	}
}
func (broker *Broker) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
	// Make sure that the writer supports flushing.
	flusher, ok := rw.(http.Flusher)
	if !ok {
		http.Error(rw, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}
	rw.Header().Set("Content-Type", "text/event-stream")
	rw.Header().Set("Cache-Control", "no-cache")
	rw.Header().Set("Connection", "keep-alive")
	rw.Header().Set("Access-Control-Allow-Origin", "*")

	// Each connection registers its own message channel with the Broker's connections registry
	messageChan := make(chan Message)
	// Signal the broker that we have a new connection
	broker.newClients <- messageChan
	// Remove this client from the map of connected clients
	// when this handler exits.
	// This will not be called until the next push from liq as we are currently blocking on messageChan
	defer func() {
		broker.closingClients <- messageChan
	}()
	// Listen to connection close and un-register messageChan
	notify := rw.(http.CloseNotifier).CloseNotify()
	// Push Loop
	for {
		select {
		case <-notify: // non-blocking
			return
		default:
			// Write to the ResponseWriter
			// Server Sent Events compatible
			message := <-messageChan
			fmt.Fprintf(rw, "event: %s\ndata: %s\n\n", message.Event, message.Message) // blocking
			// Flush the data immediatly instead of buffering it for later.
			flusher.Flush()
		}
	}
}
