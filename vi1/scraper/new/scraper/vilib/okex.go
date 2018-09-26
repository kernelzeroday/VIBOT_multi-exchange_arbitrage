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
	"sort"
	"github.com/tidwall/gjson"

	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Okex struct {
		*Exchange
		NetTransport *http.Transport
		NetClient    *http.Client
	}
	OkexCon struct {
		Okex
		Pair   string
		Time int64

		Buffer []*OkexData
	}
	OkexGet struct {
		Time int64          `json:"timestamp"`
		Asks   []OkexDepth `json:"sell"`
		Bids   []OkexDepth `json:"buy"`
	}
	OkexData struct {
		Channel   string         `json:"channel"`
		Time    int64          `json:"timestamp"`
		Bids    []OkexDepthUpdate `json:"bids"`
		Asks    []OkexDepthUpdate `json:"asks"`

	}
	OkexDepthUpdate struct {
		Rate, Amount	decimal.Decimal
	}
	OkexDepth struct {
		Rate, Amount decimal.Decimal
	}
)

func NewOkex(api, secret string) *Okex {
	okex := &Okex{
		Exchange: NewExchange("okex", map[string]string{
			"BTC_ETH":  "btc_eth",
			"BTC_XRP":  "btc_xrp",
			"BTC_XLM":  "btc_xlm",
			"BTC_NEO":  "btc_neo",
			"BTC_DASH": "btc_dash",
			"BTC_XMR":  "btc_xmr",
			"BTC_LSK":  "btc_lsk",
			"BTC_ADA":  "btc_ada",
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
	okex.Fee = decimal.New(10, -4)
	return okex
}
func (self *Okex) newOkexCon(pair string) *OkexCon {
	return &OkexCon{
		Okex: *self,
		Pair:    pair,
		Time:  0,
		Buffer:  make([]*OkexData, 0),
	}
}

func (k *OkexDepth) UnmarshalJSON(data []byte) error {
	tmp_arr := []interface{}{&k.Rate, &k.Amount}
	err := json.Unmarshal(data, &tmp_arr)
	if err != nil {
		return err
	}
	return nil
}

func (self *OkexCon) parseGet(pair string, msg []byte) bool {
	ts := time.Now().UnixNano()
	var res OkexGet
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
			seq := res.Time
			if len(self.Buffer) > 0 {
				for _, buf := range self.Buffer {
					if buf.Time <= (seq+1) && buf.Time >= (seq+1) {
						// update the book
						ts := buf.Time * 1000000
						for _, v := range buf.Asks {
							book.UpdateAsk(v.Rate, v.Amount, ts)
						}
						for _, v := range buf.Bids {
							book.UpdateBid(v.Rate, v.Amount, ts)
						}
						log.Printf("Replay Buffer: Current %d, Buffer %d, Buffer Next %d", seq, buf.Time)
						seq = buf.Time
					}
				}
			}
			self.OrderBooks[pair] = book
			self.Time = seq
			return true
		}
	}
	log.Printf("Okex Error: Could not parse Snapshot JSON:")
	return false
}

func (self *OkexCon) parse(msg []byte) bool {
	Timestamp := gjson.Get(string(msg), "[0].data.timestamp").Int()
	Asks := gjson.Get(string(msg), "[0].data.asks").Raw()
	Bids := gjson.Get(string(msg), "[0].data.bids").Raw()
	Channel := gjson.Get(string(msg), "[0].channel")
	symbol := strings.Replace(Channel.String(), "ok_sub_spot_", "", -1)
	symbol = strings.Replace(symbol, "_depth_20", "", -1)
	pair := strings.ToLower(symbol)
	if book, ok := self.OrderBooks[pair]; ok {
		ts := Timestamp * 1000000
		if Timestamp <= (self.Time+1) && Timestamp >= (self.Time+1) {
			self.Time = Timestamp
			for _, v := range Asks {
				book.UpdateAsk(v[0], v[1], ts)
			}
			for _, v := range Bids {
				book.UpdateBid(v[0], v[1], ts)
			}
		} else if Timestamp > (self.Time + 1) {
			// We've missed data, restart connection
			log.Printf("Okex Error: Sequence Mismatch: Received %s, expected %s", Timestamp, self.Time+1)
			return false
		}
	}
	return true
}

func (self *OkexCon) getBook(pair string) {
	URL := fmt.Sprintf("https://www.okex.com/api/v1/depth.do?symbol=%s", strings.ToUpper(pair))
	if rsp, err := self.NetClient.Get(URL); err == nil {
		defer rsp.Body.Close()
		if body, err := ioutil.ReadAll(rsp.Body); err == nil {
			ok := self.parseGet(pair, body)
			if ok {
				return
			}
		}
		log.Printf("Okex Error: Unable to read OrderBook reponse body.")
	}
	log.Printf("Okex Error: Unable to receive OrderBook, retrying.")

	time.Sleep(time.Second * 5)
	go self.getBook(pair)
	return
}

func (self *OkexCon) subscribe() {
	if pair, ok := self.PairMap[self.Pair]; ok {
		URL := fmt.Sprintf("wss://real.okex.com:10441/websocket")
		ws, _, err := websocket.DefaultDialer.Dial(URL, nil)

		formattedpair := strings.Split(pair, "_")
		sort.Sort(sort.Reverse(sort.StringSlice(formattedpair)))
		revpair := strings.Join(formattedpair, "_")

		SUBMSG := fmt.Sprintf("{'event':'addChannel','channel':'ok_sub_spot_%s_depth_20'}", revpair)
		ws.WriteMessage(websocket.TextMessage, []byte(SUBMSG))
		if err != nil {
			log.Println("Okex Error: Unable to  dial", pair, "websocket:", err, "Reconnecting in 10s...")
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
				log.Println("Okex Error: Could not read from websocket", err, "Reconnecting in 10s...")
				time.Sleep(10 * time.Second)
				go self.subscribe()
				return
			}
			ok := self.parse(message)
			if !ok {
				log.Printf("Okex: Encountered an on %s connection, clearing book and restarting", self.Pair)
				if book, ok := self.OrderBooks[pair]; ok {
					book.Clear()
				}
				self.Time = 0
				go self.subscribe()
				return
			}
		}
	}
}
func (self *Okex) Scrape() {
	// Subscribes
	go func() {
		for _, val := range Pairs {
			time.Sleep(time.Second)
			go self.newOkexCon(val.Name).subscribe()
		}
	}()
}

