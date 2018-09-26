package vilib

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"strings"
	"time"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Binance struct {
		*Exchange
		NetTransport *http.Transport
		NetClient    *http.Client
	}
	BinanceCon struct {
		Binance
		Pair   string
		LastID int64
		Buffer []*BinanceData
	}
	BinanceGet struct {
		LastID int64          `json:"lastUpdateId"`
		Asks   []BinanceDepth `json:"asks"`
		Bids   []BinanceDepth `json:"bids"`
	}
	BinanceData struct {
		Event   string         `json:"e"`
		Time    int64          `json:"E"`
		Symbol  string         `json:"s"`
		FirstID int64          `json:"U"`
		LastID  int64          `json:"u"`
		Bids    []BinanceDepth `json:"b"` // []{rate, amount, ignore}
		Asks    []BinanceDepth `json:"a"` // []{rate, amount, ignore}
	}
	BinanceDepth struct {
		Rate, Amount decimal.Decimal
		Extra        []string
	}
)

func NewBinance(api, secret string) *Binance {
	binance := &Binance{
		Exchange: NewExchange("binance", map[string]string{
			"USD_BTC": "btcusdt",
			"USD_ETH": "ethusdt",
			"USD_NEO": "neousdt",

			"BTC_ETH":  "ethbtc",
			"BTC_XRP":  "xrpbtc",
			"BTC_XLM":  "xlmbtc",
			"BTC_NEO":  "neobtc",
			"BTC_DASH": "dashbtc",
			"BTC_XMR":  "xmrbtc",
			"BTC_LSK":  "lskbtc",
			"BTC_ADA":  "adabtc",
		}),
		NetClient: &http.Client{
			Timeout: time.Second * 6,
			Transport: &http.Transport{
				Dial: (&net.Dialer{
					Timeout: 3 * time.Second,
				}).Dial,
				TLSHandshakeTimeout: 3 * time.Second,
			},
		},
	}
	binance.Fee = decimal.New(10, -4)
	return binance
}
func (self *Binance) newBinanceCon(pair string) *BinanceCon {
	return &BinanceCon{
		Binance: *self,
		Pair:    pair,
		LastID:  0,
		Buffer:  make([]*BinanceData, 0),
	}
}

func (k *BinanceDepth) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Rate, &k.Amount, &k.Extra}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (self *BinanceCon) parseGet(pair string, msg []byte) bool {
	ts := time.Now().UnixNano()
	var res BinanceGet
	if err := json.Unmarshal(msg, &res); err == nil {
		// Initialise the book here.
		if book, ok := self.OrderBooks[pair]; ok {
			//Sequence used for sync with websokets
			for _, v := range res.Asks {
				book.UpdateAsk(v.Rate, v.Amount, ts)
			}
			for _, v := range res.Bids {
				book.UpdateBid(v.Rate, v.Amount, ts)
			}
			seq := res.LastID
			if len(self.Buffer) > 0 {
				for _, buf := range self.Buffer {
					if buf.FirstID <= (seq+1) && buf.LastID >= (seq+1) {
						// update the book
						ts := buf.Time * 1000000
						for _, v := range buf.Asks {
							book.UpdateAsk(v.Rate, v.Amount, ts)
						}
						for _, v := range buf.Bids {
							book.UpdateBid(v.Rate, v.Amount, ts)
						}
						log.Printf("Replay Buffer: Current %d, Buffer %d, Buffer Next %d", seq, buf.FirstID, buf.LastID)
						seq = buf.LastID
					}
				}
			}
			self.OrderBooks[pair] = book
			self.LastID = seq
			return true
		}
	}
	log.Printf("Binance Error: Could not parse Snapshot JSON:")
	return false
}

func (self *BinanceCon) parse(msg []byte) bool {
	var res BinanceData
	if err := json.Unmarshal(msg, &res); err == nil {
		pair := strings.ToLower(res.Symbol)
		if book, ok := self.OrderBooks[pair]; ok {
			ts := res.Time * 1000000
			if self.LastID == 0 {
				// Add to replay buffer
				self.Buffer = append(self.Buffer, &res)
			} else {
				if res.FirstID <= (self.LastID+1) && res.LastID >= (self.LastID+1) {
					self.LastID = res.LastID
					for _, v := range res.Asks {
						book.UpdateAsk(v.Rate, v.Amount, ts)
					}
					for _, v := range res.Bids {
						book.UpdateBid(v.Rate, v.Amount, ts)
					}
				} else if res.FirstID > (self.LastID + 1) {
					// We've missed data, restart connection
					log.Printf("Binance Error: Sequence Mismatch: Received %s, expected %s", res.FirstID, self.LastID+1)
					return false
				}
			}
		}
	} else {
		log.Printf("Binance Error: Could not parse JSON: %s\n With data: %s", err, msg)
	}
	return true
}

func (self *BinanceCon) getBook(pair string) {
	URL := fmt.Sprintf("https://api.binance.com/api/v1/depth?symbol=%s", strings.ToUpper(pair))
	if rsp, err := self.NetClient.Get(URL); err == nil {
		defer rsp.Body.Close()
		if body, err := ioutil.ReadAll(rsp.Body); err == nil {
			ok := self.parseGet(pair, body)
			if ok {
				return
			}
		}
		log.Printf("Binance Error: Unable to read OrderBook reponse body.")
	}
	log.Printf("Binance Error: Unable to receive OrderBook, retrying.")

	time.Sleep(time.Second * 5)
	go self.getBook(pair)
	return
}

func (self *BinanceCon) subscribe() {
	if pair, ok := self.PairMap[self.Pair]; ok {
		URL := fmt.Sprintf("wss://stream.binance.com:9443/ws/%s@depth", pair)

		ws, _, err := websocket.DefaultDialer.Dial(URL, nil)
		if err != nil {
			log.Println("Binance Error: Unable to  dial", pair, "websocket:", err, "Reconnecting in 10s...")
			time.Sleep(10 * time.Second)
			go self.subscribe()
			return
		}
		defer ws.Close()
		// Get Orderbook via REST
		go self.getBook(pair)

		for {
			_, message, err := ws.ReadMessage()
			if err != nil {
				log.Println("Binance Error: Could not read from websocket", err, "Reconnecting in 10s...")
				time.Sleep(10 * time.Second)
				go self.subscribe()
				return
			}
			ok := self.parse(message)
			if !ok {
				log.Printf("Bittrex: Encountered an on %s connection, clearing book and restarting", self.Pair)
				if book, ok := self.OrderBooks[pair]; ok {
					book.Clear()
				}
				self.LastID = 0
				go self.subscribe()
				return
			}
		}
	}
}
func (self *Binance) Scrape() {
	// Subscribes
	go func() {
		for _, val := range Pairs {
			time.Sleep(time.Second)
			go self.newBinanceCon(val.Name).subscribe()
		}
	}()
}
