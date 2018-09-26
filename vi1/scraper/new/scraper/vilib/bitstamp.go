package vilib

import (
	"encoding/json"
	"log"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Bitstamp struct {
		*Exchange
	}
	BitstampEvent struct {
		Event   string       `json:"event"`
		Channel string       `json:"channel,omitempty"`
		Data    BitstampData `json:"data,omitempty"`
	}
	BitstampData struct {
		Asks    [][2]decimal.Decimal `json:"asks,omitempty"`
		Bids    [][2]decimal.Decimal `json:"bids,omitempty"`
		Channel string               `json:"channel,omitempty"`
	}
)

func NewBitstamp(api, secret string) *Bitstamp {
	bitstamp := &Bitstamp{
		Exchange: NewExchange("bitstamp", map[string]string{
			"USD_BTC": "order_book",
			"USD_ETH": "order_book_ethusd",
			"USD_XRP": "order_book_xrpusd",
			// "USD_XLM":
			// "USD_NEO":
			// "USD_DASH":
			// "USD_XMR":
			// "USD_LSK":

			"BTC_ETH": "order_book_ethbtc",
			"BTC_XRP": "order_book_xrpbtc",
			// "BTC_XLM":
			// "BTC_NEO":
			// "BTC_DASH":
			// "BTC_XMR":
			// "BTC_LSK":
		}),
	}
	bitstamp.Fee = decimal.New(25, -4)
	return bitstamp
}

func (k *BitstampEvent) UnmarshalJSON(raw []byte) error {
	var tmp struct {
		Event   string `json:"event"`
		Channel string `json:"channel,omitempty"`
		DataRaw string `json:"data,omitempty"`
	}
	if err := json.Unmarshal(raw, &tmp); err != nil {
		log.Printf("Error %s", err)
		return err
	}
	var data BitstampData
	if err := json.Unmarshal([]byte(tmp.DataRaw), &data); err != nil {
		log.Printf("Error %s", err)
		return err
	}
	*k = BitstampEvent{
		Event:   tmp.Event,
		Channel: tmp.Channel,
		Data:    data,
	}
	return nil
}

func (self *Bitstamp) parse(msg []byte) {
	var data BitstampEvent
	if err := json.Unmarshal(msg, &data); err == nil {
		switch data.Event {
		case "pusher_internal:subscription_succeeded":
			_, ok := self.OrderBooks[data.Channel]
			if !ok {
				log.Printf("Bitstamp Error: Could not find book: %s", data.Channel)
				return
			}
		case "data":
			if book, ok := self.OrderBooks[data.Channel]; ok {
				// Clear Current Books
				book.Asks = make(map[string]*OrderBookData)
				book.Bids = make(map[string]*OrderBookData)
				ts := time.Now().UnixNano()
				c := make(chan bool)
				go func() {
					for i, v := range data.Data.Asks {
						var key = v[0].String()
						book.Asks[key] = &OrderBookData{
							Key:       key,
							Price:     v[0],
							Qty:       v[1],
							Timestamp: ts,
						}
						if i == 0 {
							book.SetMinAsk(book.Asks[key])
						}
					}
					c <- true
				}()
				for i, v := range data.Data.Bids {
					var key = v[0].String()
					book.Bids[key] = &OrderBookData{
						Key:       key,
						Price:     v[0],
						Qty:       v[1],
						Timestamp: ts,
					}
					if i == 0 {
						book.SetMaxBid(book.Bids[key])
					}
				}
				<-c
				return
			}
			log.Println("Bitstamp Error: Could not find book %s", data.Channel)
		}
	}
}

func (self *Bitstamp) subscribe(ws *websocket.Conn, currency string) {
	if pair, ok := self.PairMap[currency]; ok {
		time.Sleep(time.Second)
		sub := &BitstampEvent{
			Event: "pusher:subscribe",
			Data: BitstampData{
				Channel: pair,
			},
		}
		err := ws.WriteJSON(sub)
		if err != nil {
			log.Println("Bitstamp Error: Could not write to websocket", err)
			time.Sleep(10 * time.Second)
			go self.subscribe(ws, currency)
			return
		}
	}
}
func (self *Bitstamp) Scrape() {
	URL := "wss://ws.pusherapp.com/app/0ea60078504a5d9773ab?protocol=7&client=js&version=4.1.0&flash=false"
	ws, _, err := websocket.DefaultDialer.Dial(URL, nil)
	if err != nil {
		log.Println("Bitfinex Error: Could not dial websocket:", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	defer ws.Close()
	// Subscribes
	go func() {
		for _, val := range Pairs {
			self.subscribe(ws, val.Name)
		}
	}()
	for {
		_, msg, err := ws.ReadMessage()
		if err != nil {
			log.Println("Bitstamp Error: Could not read from websocket", err, "Reconnecting in 10s...")
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(msg)
	}

}
