package vilib

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Cex struct {
		*Exchange
		Scales map[string]decimal.Decimal
	}
	CexRequest struct {
		Event string          `json:"e"`
		Auth  *CexAuth        `json:"auth,omitempty"`
		Rooms []string        `json:"rooms,omitempty"`
		Data  json.RawMessage `json:"data,omitempty"`
		Oid   string          `json:"oid,omitempty"`
	}
	CexAuth struct {
		Key       string `json:"key"`
		Signature string `json:signature`
		Timestamp int64  `json:timestamp`
	}
	CexResponse struct {
		Event     string          `json:"e"`
		Data      json.RawMessage `json:"data"`
		Ok        string          `json:"ok"`
		Timestamp int64           `json:"timestamp"`
	}
	CexBook struct {
		Pair      string              `json:"pair"`
		BuyTotal  int64               `json:"buy_total"`
		SellTotal int64               `json:"sell_total"`
		ID        int64               `json:"id"`
		Buy       [][]decimal.Decimal `json:"buy"`
		Sell      [][]decimal.Decimal `json:"sell"`
	}
)

func NewCex(api, secret string) *Cex {
	cex := &Cex{
		Exchange: NewExchange("cex", map[string]string{
			//"USD_BTC": "BTC:USD",
			//"USD_ETH": "ETH:USD",
			//"USD_XRP": "XRP:USD",
			//"USD_XLM": "XLM:USD",
			//"USD_ZEC": "USD:ZEC",
			// "USD_NEO":
			//"USD_DASH": "DASH:USD",
			// "USD_XMR":
			// "USD_LSK":
			//"BTC_BCH": "BTC:BCH",
			"BTC_ETH": "ETH:BTC",
			"BTC_ZEC": "ZEC:BTC",
			"BTC_XRP": "XRP:BTC",
			"BTC_XLM": "XLM:BTC",
			// "BTC_NEO":
			"BTC_DASH": "DASH:BTC",
			// "BTC_XMR":
			// "BTC_LSK":
		}),
		Scales: map[string]decimal.Decimal{
			//"BTC:USD": decimal.New(1, -8), // Satoshi = 1 exp(-8)
			//"ETH:USD": decimal.New(1, -2), // Cent = 1 exp(-2)
			//"XRP:USD": decimal.New(1, -6), // Drop = 1 exp(-6)
			//"XLM:USD": decimal.New(1, -7), // Stroop = 1 exp(-7)
			// "USD_NEO":
			//"DASH:USD": decimal.New(1, -8), // Duff = 1 exp(-8)
			// "USD_XMR":
			// "USD_LSK":

			"ETH:BTC": decimal.New(1, -2), // Cent = 1 exp(-2)
			"XRP:BTC": decimal.New(1, -6), // Drop = 1 exp(-6)
			"XLM:BTC": decimal.New(1, -7), // Stroop = 1 exp(-7)
			// "BTC_NEO":
			"DASH:BTC": decimal.New(1, -8), // Duff = 1 exp(-8)
			"ZEC:BTC": decimal.New(1, -2), // Duff = 1 exp(-8)
			// "BTC_XMR":
			// "BTC_LSK":
		},
	}
	cex.Fee = decimal.New(15, -4)
	cex.Key = api
	cex.Secret = secret
	return cex
}

func (self *Cex) parse(msg []byte, ws *websocket.Conn) {
	var res CexResponse
	err := json.Unmarshal(msg, &res)
	if err != nil {
		log.Printf("CEX Error: Could not unmarshal: %s", err)
		return
	}
	switch res.Event {
	case "md_update": // Private Orderbook update

	case "order-book-subscibe": // Private Orderbook Subscribe

	case "auth":
		log.Printf("Auth Response: %s", msg)
		// TODO Subscribe to books

	case "md": // Public Method
		data := new(CexBook)
		if err = json.Unmarshal(res.Data, &data); err == nil {
			book, ok := self.OrderBooks[data.Pair]
			if !ok {
				log.Printf("CEX Error: Could not find book: %s", data.Pair)
				return
			}
			if scale, ok := self.Scales[data.Pair]; ok {
				// Clear Current Books
				book.Asks = make(map[string]*OrderBookData)
				book.Bids = make(map[string]*OrderBookData)
				ts := time.Now().UnixNano()
				for i, v := range data.Sell {
					var key = v[0].String()
					book.Asks[key] = &OrderBookData{
						Key:       key,
						Price:     v[0],
						Qty:       v[1].Mul(scale),
						Timestamp: ts,
					}
					if i == 0 {
						book.SetMinAsk(book.Asks[key])
					}
				}
				for i, v := range data.Buy {
					var key = v[0].String()
					book.Bids[key] = &OrderBookData{
						Key:       key,
						Price:     v[0],
						Qty:       v[1].Mul(scale),
						Timestamp: ts,
					}
					if i == 0 {
						book.SetMaxBid(book.Bids[key])
					}
				}
				self.OrderBooks[data.Pair] = book
			} else {
				log.Printf("CEX Error: No currency scale found.")
			}
		} else {
			log.Printf("CEX Error: Could not unmarshal: %s", err)
		}
	}
}

func (self *Cex) Scrape() {
	subs := make([]string, 0)
	for _, v := range Pairs {
		if pair, ok := self.PairMap[v.Name]; ok {
			pair = fmt.Sprintf("pair-%s", strings.Replace(pair, ":", "-", 1))
			subs = append(subs, pair)
		}
	}

	ws, _, err := websocket.DefaultDialer.Dial("wss://ws.cex.io/ws/", nil)
	if err != nil {
		log.Printf("CEX Error: Could not dial websocket: %s", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	defer ws.Close()

	request := new(CexRequest)
	if self.Key != "" && self.Secret != "" {
		ts := time.Now().Unix()
		msg := fmt.Sprintf("%d%s", ts, self.Key)
		hash := hmac.New(sha256.New, []byte(self.Secret))
		hash.Write([]byte(msg))
		sig := hex.EncodeToString(hash.Sum(nil))
		log.Printf("TS: %d, Key: %s, Secret: %s, Sig: %s", ts, self.Key, self.Secret, sig)
		auth := &CexAuth{
			Key:       self.Key,
			Signature: sig,
			Timestamp: ts,
		}
		request.Event = "auth"
		request.Auth = auth
	} else {
		request.Event = "subscribe"
		request.Rooms = subs
	}
	err = ws.WriteJSON(request)
	if err != nil {
		log.Printf("CEX Error: Could not write to websocket: %s", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}

	for {
		_, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("CEX Error: Could not read from websocket: %s", err)
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(message, ws)
	}
}
