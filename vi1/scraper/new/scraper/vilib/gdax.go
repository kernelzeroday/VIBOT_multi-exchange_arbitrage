package vilib

import (
	"encoding/json"
	"log"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Gdax struct {
		*Exchange
	}
	GdaxRequest struct {
		Type       string   `json:"type"`
		ProductIds []string `json:"product_ids"`
		Channels   []string `json:"channels"`
	}
	GdaxResponse struct {
		Type        string                 `json:"type"`          // Common
		Message     string                 `json:"message"`       // Types: error
		Channels    []GdaxResponseChannels `json:"channels"`      // Types: subscriptions
		ProductId   string                 `json:"product_id"`    // Types: heartbeat, ticker, snapshot, l2update
		Asks        [][2]decimal.Decimal   `json:"asks"`          // Types: snapshot
		Bids        [][2]decimal.Decimal   `json:"bids"`          // Types: snapshot
		Changes     []GdaxChanges          `json:"changes"`       // Types: l2update
		LastTradeId int64                  `json:"last_trade_id"` // Types: heartbeat
		Sequence    int64                  `json:"sequence"`      // Types: heartbeat, ticker
		Time        string                 `json:"time"`          // Types: heartbeat, ticker
		TradeId     int64                  `json:"trade_id"`      // Types: ticker
		Price       decimal.Decimal        `json:"price"`         // Types: ticker
		Side        string                 `json:"side"`          // Types: ticker | buy = taker, sell = maker
		LastSize    decimal.Decimal        `json:"last_size"`     // Types: ticker
		BestBid     decimal.Decimal        `json:"best_bid"`      // Types: ticker
		BestAsk     decimal.Decimal        `json:"best_ask"`      // Types: ticker
	}
	GdaxChanges struct {
		Type       string
		Price, Qty decimal.Decimal
	}
	GdaxResponseChannels struct {
		Name       string   `json:"name"`
		ProductIds []string `json:"product_ids"`
	}
)

func NewGdax(api, secret string) *Gdax {
	gdax := &Gdax{
		Exchange: NewExchange("gdax", map[string]string{
			"USD_BTC": "BTC-USD",
			"USD_ETH": "ETH-USD",
			// "USD_XRP":
			// "USD_XLM":
			// "USD_NEO":
			// "USD_DASH":
			// "USD_XMR":
			// "USD_LSK":

			"BTC_ETH": "ETH-BTC",
			// "BTC_XRP":
			// "BTC_XLM":
			// "BTC_NEO":
			// "BTC_DASH":
			// "BTC_XMR":
			// "BTC_LSK":
		}),
	}
	gdax.Fee = decimal.New(25, -4)
	return gdax
}

// Methods
func (k *GdaxChanges) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Type, &k.Price, &k.Qty}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (self *Gdax) parse(msg []byte) {
	var resp GdaxResponse
	err := json.Unmarshal(msg, &resp)
	if err != nil {
		log.Printf("GDAX ERROR: Unable to unmarshal: %s", err)
		return
	}
	timestamp := time.Now().UnixNano()
	switch resp.Type {
	case "l2update":
		if g, ok := self.OrderBooks[resp.ProductId]; ok {
			for _, v := range resp.Changes {
				switch v.Type {
				case "buy": // Buy at an ask level
					//log.Printf("BUY: Price: %s, Amount: %s", v[1], v[2])
					g.UpdateBid(v.Price, v.Qty, timestamp)
				case "sell": // Sell at a bid level
					//log.Printf("SELL: Price: %s, Amount: %s", v[1], v[2])
					g.UpdateAsk(v.Price, v.Qty, timestamp)
				}
			}
		} else {
			log.Printf("GDAX: %s Could not fine orderbook", resp.ProductId)
		}

	case "ticker":
	case "heartbeat":
	case "snapshot":
		book, ok := self.OrderBooks[resp.ProductId]
		if !ok {
			log.Printf("GDAX Error: Could not find orderbook: %s", resp.ProductId)
			return
		}
		for _, v := range resp.Asks {
			book.UpdateAsk(v[0], v[1], timestamp)
		}
		for _, v := range resp.Bids {
			book.UpdateBid(v[0], v[1], timestamp)
		}
	case "subscriptions":
	case "unsubscribe":
	case "error":
	}
}

func (self *Gdax) Scrape() {
	ws, _, err := websocket.DefaultDialer.Dial("wss://ws-feed.gdax.com", nil)
	if err != nil {
		log.Printf("GDAX Error: Could not dial websocket: %s", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	defer ws.Close()

	pairs := make([]string, 0)
	for _, val := range Pairs {
		if pair, ok := self.PairMap[val.Name]; ok {
			pairs = append(pairs, pair)
		}
	}
	request := &GdaxRequest{
		Type:       "subscribe",
		ProductIds: pairs,
		Channels:   []string{"heartbeat", "ticker", "level2"},
	}
	err = ws.WriteJSON(request)
	if err != nil {
		log.Printf("GDAX Error: Could not write to websocket: %s", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	// Read Loop
	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("GDAX Error: Could not read from websocket: %s", err)
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(message)
	}
}
