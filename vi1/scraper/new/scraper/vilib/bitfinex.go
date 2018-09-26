/* TODO
 * Implement orderbook handling
 * Implement proper exchange objects
 * Accept a string of currencypairs
 */
package vilib

import (
	"encoding/json"
	"log"
	"strings"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Bitfinex struct {
		*Exchange
		ChannelMap map[int64]string
	}
	BitfinexEvent struct {
		Event     string `json:"event"`
		Version   int64  `json:"version,omitempty"`
		Channel   string `json:"channel,omitempty"`
		ChannelID int64  `json:"chanId,omitempty"`
		Symbol    string `json:"symbol,omitempty"`
		Pair      string `json:"pair,omitempty"`
		Message   string `json:"msg,omitempty"`
		Code      string `json:"code,omitempty"`
		Precision string `json:"prec,omitempty"`
		Frequency string `freq:"prec,omitempty"`
		Length    string `len:"prec,omitempty"`
	}
	BitfinexSnapshot struct {
		ID   int64
		Data [][3]decimal.Decimal
	}
	BitfinexUpdate struct {
		ID   int64
		Data [3]decimal.Decimal
	}
)

func NewBitfinex(api, secret string) *Bitfinex {
	bitfinex := &Bitfinex{
		Exchange: NewExchange("bitfinex", map[string]string{
			"USD_BTC": "tBTCUSD",
			"USD_ETH": "tETHUSD",
			"USD_XRP": "tXRPUSD",
			// "USD_XLM":
			"USD_NEO":  "tNEOUSD",
			"USD_DASH": "tDSHUSD",
			"USD_XMR":  "tXMRUSD",
			// "USD_LSK":

			"BTC_ETH": "tETHBTC",
			"BTC_XRP": "tXRPBTC",
			// "BTC_XLM":
			"BTC_NEO":  "tNEOBTC",
			"BTC_DASH": "tDSHBTC",
			"BTC_XMR":  "tXMRBTC",
			// "BTC_LSK":
		}),
		ChannelMap: make(map[int64]string),
	}
	bitfinex.Fee = decimal.New(20, -4)
	return bitfinex
}

func (k *BitfinexSnapshot) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.ID, &k.Data}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (k *BitfinexUpdate) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.ID, &k.Data}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (self *Bitfinex) parse(msg []byte) {
	ts := time.Now().UnixNano()

	var update BitfinexUpdate
	if err := json.Unmarshal(msg, &update); err == nil {
		if pair, ok := self.ChannelMap[update.ID]; ok {
			if book, ok := self.OrderBooks[pair]; ok {
				qty := update.Data[2]
				if update.Data[1].Sign() == 0 {
					qty = decimal.Zero
				}
				if update.Data[2].Sign() > 0 {
					// Bid
					book.UpdateBid(update.Data[0], qty, ts)
				} else {
					// Asks
					book.UpdateAsk(update.Data[0], qty.Neg(), ts)
				}
			} else {
				log.Printf("Bitfinex Error: Book not found for %s", pair)
			}
		} else {
			log.Printf("Bitfinex Error: Pair not found for %s", update.ID)
		}
		return
	}
	if strings.Contains(string(msg), "\"hb\"") {
		// heartbeat
		return
	}
	var snapshot BitfinexSnapshot
	if err := json.Unmarshal(msg, &snapshot); err == nil {
		pair, ok := self.ChannelMap[snapshot.ID]
		if !ok {
			log.Printf("Bitfinex Error: Could not fine snapshot: %+v", snapshot)
			return
		}
		book, ok := self.OrderBooks[pair]
		if !ok {
			log.Printf("Bitfinex Error: Could not find book: %s", pair)
			return
		}
		for _, v := range snapshot.Data {
			if v[2].Sign() > 0 {
				// Bid
				book.UpdateBid(v[0], v[2], ts)
			} else {
				// Asks
				book.UpdateAsk(v[0], v[2].Neg(), ts)
			}
		}
		return
	}
	var event BitfinexEvent
	if err := json.Unmarshal(msg, &event); err == nil {
		if event.Event == "subscribed" {
			self.ChannelMap[event.ChannelID] = event.Symbol
		}
		log.Printf("Bitfinex Event: %+v", event) // TODO handle other events
		return
	}
	log.Printf("Bitfinex Error: Could not parse event: %s", msg)
}

func (self *Bitfinex) subscribe(ws *websocket.Conn, currency string) {
	if pair, ok := self.PairMap[currency]; ok {
		time.Sleep(time.Second)
		sub := &BitfinexEvent{
			Event:     "subscribe",
			Channel:   "book",
			Symbol:    pair,
			Precision: "P0",
			Frequency: "F0",
			Length:    "100",
		}
		err := ws.WriteJSON(sub)
		if err != nil {
			log.Println("Bitfinex Error: Could not write to websocket:", err)
		}
	}
}

func (self *Bitfinex) Scrape() {
	c, _, err := websocket.DefaultDialer.Dial("wss://api.bitfinex.com/ws/2", nil)
	if err != nil {
		log.Println("Bitfinex Error: Could not dial websocket:", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	defer c.Close()

	go func() {
		for _, val := range Pairs {
			self.subscribe(c, val.Name)
		}
	}()

	for {
		_, message, err := c.ReadMessage()
		if err != nil {
			log.Println("Bitfinex Error: Could not read from websocket:", err)
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(message)
	}
}
