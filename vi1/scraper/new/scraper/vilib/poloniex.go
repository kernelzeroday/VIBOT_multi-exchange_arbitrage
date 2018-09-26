package vilib

import (
	"encoding/json"
	"log"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Poloniex struct {
		*Exchange
		IDs map[int64]string
	}
	PoloniexRequest struct {
		Command string `json:"command"`
		Channel string `json:"channel"`
	}
	PoloniexResponse struct {
		Id, Sequence int64
		Data         []json.RawMessage
	}
	PoloniexUpdate struct {
		Id           string
		Rate, Amount decimal.Decimal
		IsBid        int
	}
	PoloniexInit struct {
		Type string
		Data PoloniexInitData
	}
	PoloniexInitData struct {
		Pair string                                 `json:"currencyPair"`
		Book [2]map[decimal.Decimal]decimal.Decimal `json:"orderBook"`
	}
)

func NewPoloniex(api, secret string) *Poloniex {
	poloniex := &Poloniex{
		Exchange: NewExchange("poloniex", map[string]string{
			"USDT_BTC": "USDT_BTC",
			"USDT_ETH": "USDT_ETH",
			"USDT_XRP": "USDT_XRP",
			// "USD_XLM":
			// "USD_NEO":
			"USDT_DASH": "USDT_DASH",
			"USDT_XMR": "USDT_XMR",
			// "USD_LSK":
			"BTC_NEM": "BTC_XEM",
			"BTC_ETH": "BTC_ETH",
			"BTC_XRP": "BTC_XRP",
			"BTC_XLM": "BTC_STR",
			// "BTC_NEO":
			"BTC_DASH": "BTC_DASH",
			"BTC_XMR": "BTC_XMR",
			"BTC_LSK": "BTC_LSK",
                        "ETH_ETC": "ETH_ETC",
                        //"ETH_LTC": "ETH_LTC",
                        "ETH_OMG": "ETH_OMG",
                        "ETH_GNT": "ETH_GNT",
			"BTC_ZEC": "BTC_ZEC",
			"BTC_LTC": "BTC_LTC",
			"BTC_ETC": "BTC_ETC",
			"BTC_OMG": "BTC_OMG",
		}),
		IDs: make(map[int64]string),
	}
	poloniex.Fee = decimal.New(25, -4)
	return poloniex
}

// Methods
func (k *PoloniexResponse) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Id, &k.Sequence, &k.Data}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (k *PoloniexInit) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Type, &k.Data}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (k *PoloniexUpdate) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Id, &k.IsBid, &k.Rate, &k.Amount}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (self *Poloniex) parse(msg []byte) {
	var resp PoloniexResponse
	err := json.Unmarshal(msg, &resp)
	if err != nil {
		log.Printf("Poloniex Error: Unable to unmarshal: %s", err)
		return
	}

	for _, value := range resp.Data {
		var stub string
		stub_arr := []interface{}{&stub}
		err := json.Unmarshal(value, &stub_arr)
		if err != nil {
			log.Printf("Poloniex Error: Unable to unmarshal: %s", err)
		}
		timestamp := time.Now().UnixNano()
		switch stub {
		case "o": // Order Update
			var update PoloniexUpdate
			err := json.Unmarshal(value, &update)
			if err != nil {
				log.Printf("Poloniex Error: Unable to unmarshal: %s", err)
			}
			//log.Printf("Update: %s", update)

			if pair, ok := self.IDs[resp.Id]; ok {
				if book, ok := self.OrderBooks[pair]; ok {
					switch update.IsBid {
					case 0:
						book.UpdateAsk(update.Rate, update.Amount, timestamp)
					case 1:
						book.UpdateBid(update.Rate, update.Amount, timestamp)
					}
				} else {
					log.Printf("Poloniex Error: Cant find book %s", pair)
				}
			}

		case "t": // Trade Update
			//log.Printf("Trade")

		case "i": // Orderbook init
			log.Printf("Init")
			var init PoloniexInit
			if err := json.Unmarshal(value, &init); err == nil {
				if book, ok := self.OrderBooks[init.Data.Pair]; ok {
					// Consider manually building without running min/max
					for key, val := range init.Data.Book[0] {
					book.UpdateAsk(key, val, timestamp)
					}
					for key, val := range init.Data.Book[1] {
						book.UpdateBid(key, val, timestamp)
					}
					self.IDs[resp.Id] = init.Data.Pair
				}
			} else {
				log.Printf("Poloniex Error: Unable to unmarshal: %s", err)
			}
		}
	}
	return
}

func (self *Poloniex) subscribe(ws *websocket.Conn, currency string) {
	if pair, ok := self.PairMap[currency]; ok {
		time.Sleep(time.Second)
		sub := &PoloniexRequest{
			Command: "subscribe",
			Channel: pair,
		}
		err := ws.WriteJSON(sub)
		if err != nil {
			log.Printf("Poloniex Error: Could not write to websocket: %s", err)
			time.Sleep(10 * time.Second)
			go self.subscribe(ws, currency)
			return
		}
	}
}

func (self *Poloniex) Scrape() {
	ws, _, err := websocket.DefaultDialer.Dial("wss://api2.poloniex.com:443", nil)
	if err != nil {
		log.Printf("Poloniex Error: Could not dial websocket: %s: Reconnecting in 10s", err)
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

	// Read Loop
	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("Poloniex Error: Could not read from websocket: %s: Reconnecting in 10s", err)
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(message)
	}
}
