// TODO THIS SHIT

package vilib

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Gemini struct {
		*Exchange
	}
	GeminiCon struct {
		Gemini
		Pair     string
		Sequence int64
		Book     *OrderBook
	}
	GeminiResponse struct {
		Type        string        `json:"type"`
		EventID     int64         `json:"eventId"`
		Sequence    int64         `json:"socket_sequence"`
		Timestamp   int64         `json:"timestamp"`
		TimestampMS int64         `json:"timestampms"`
		Events      []GeminiEvent `json:"events"`
	}
	GeminiEvent struct {
		Type      string          `json:"type"`
		Side      string          `json:"side"`
		Reason    string          `json:"reason"`
		Price     decimal.Decimal `json:"price"`
		Delta     decimal.Decimal `json:"delta"`
		Remaining decimal.Decimal `json:"remaining"`
	}
)

func NewGemini(api, secret string) *Gemini {
	gemini := &Gemini{
		Exchange: NewExchange("gemini", map[string]string{
			"USD_BTC": "btcusd",
			"USD_ETH": "ethusd",
			// "USD_XRP":
			// "USD_XLM":
			// "USD_NEO":
			// "USD_DASH":
			// "USD_XMR":
			// "USD_LSK":

			"BTC_ETH": "ethbtc",
			// "BTC_XRP":
			// "BTC_XLM":
			// "BTC_NEO":
			// "BTC_DASH":
			// "BTC_XMR":
			// "BTC_LSK":
		}),
	}
	gemini.Fee = decimal.New(25, -4)
	return gemini
}
func (self *Gemini) newGeminiCon(pair string) *GeminiCon {
	return &GeminiCon{
		Gemini:   *self,
		Pair:     pair,
		Sequence: -1,
	}
}

func (self *GeminiCon) parse(msg []byte) {
	var res GeminiResponse
	err := json.Unmarshal(msg, &res)
	if err != nil {
		log.Printf("Gemini Error: Unable to unmarshal: %s", err)
		return
	}

	if res.Sequence != self.Sequence+1 {
		// Force a reconnect
		log.Printf("Sequence out of order, reconnecting") // TODO Error Channel
		return
	}
	self.Sequence = res.Sequence
	book, ok := self.OrderBooks[self.Pair]
	if !ok {
		log.Printf("Gemini Error: Could not find book: %s in: %s", self.Pair, self.OrderBooks)
		return
	}

	switch res.Type {
	case "update":
		ts := res.TimestampMS * 1000000
		for _, v := range res.Events {
			key := v.Price.String()

			switch v.Reason {
			case "initial":
				value := &OrderBookData{
					Key:       key,
					Price:     v.Price,
					Qty:       v.Remaining,
					Timestamp: ts,
				}
				// Build Book Directly
				switch v.Side {
				case "ask":
					book.Asks[key] = value
				case "bid":
					book.Bids[key] = value
				}
			default:
				// Realtime Updates
				switch v.Side {
				case "ask":
					book.UpdateAsk(v.Price, v.Remaining, ts)
				case "bid":
					book.UpdateBid(v.Price, v.Remaining, ts)
				}
			}
		}
	case "heartbeat":
		//log.Printf("Heartbeat")
	}
}

func (self *GeminiCon) subscribe() {
	time.Sleep(time.Second)
	URL := fmt.Sprintf("wss://api.gemini.com/v1/marketdata/%s?heartbeat=true", self.Pair)

	ws, _, err := websocket.DefaultDialer.Dial(URL, nil)
	if err != nil {
		log.Printf("Gemini Error: Could not dial websocket: %s", err)
		time.Sleep(10 * time.Second)
		go self.subscribe()
		return
	}
	defer ws.Close()

	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("Gemini Error: Could not read from websocket: %s", err)
			time.Sleep(10 * time.Second)
			go self.subscribe()
			return
		}
		self.parse(message)
	}
}

func (self *Gemini) Scrape() {
	// Subscribes
	go func() {
		for _, val := range Pairs {
			if pair, ok := self.PairMap[val.Name]; ok {
				go self.newGeminiCon(pair).subscribe()
			}
		}
	}()
}
