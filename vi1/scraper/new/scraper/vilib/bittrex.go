package vilib

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strconv"
	"time"

	"github.com/cardigann/go-cloudflare-scraper"
	"github.com/gorilla/websocket"
	"github.com/shopspring/decimal"
)

type (
	Bittrex struct {
		*Exchange
		CallIndex                 int64
		SubscribeMap, ResponseMap map[string]string
	}
	BittrexNegotiationResponse struct {
		Url                     string
		ConnectionToken         string
		ConnectionId            string
		KeepAliveTimeout        float32
		DisconnectTimeout       float32
		ConnectionTimeout       float32
		TryWebSockets           bool
		ProtocolVersion         string
		TransportConnectTimeout float32
		LogPollDelay            float32

		Cookie    []string
		UserAgent []string
	}
	BittrexResponse struct {
		Cursor     string            `json:"C"`
		Data       []json.RawMessage `json:"M"`
		Result     json.RawMessage   `json:"R"`
		Identifier string            `json:"I"`
		Error      string            `json:"E"`
	}
	BittrexResponseData struct {
		Hub       string                 `json:"H"`
		Method    string                 `json:"M"`
		Arguments []BittrexResponseData2 `json:"A"`
	}
	BittrexResponseData2 struct {
		Pair     string                 `json:"MarketName"`
		Sequence int64                  `json:"Nounce"`
		Buys     []BittrexResponseData3 `json:"Buys"`
		Sells    []BittrexResponseData3 `json:"Sells"`
		//Fills    []BittrexResponseData3 `json:"Fills"`
	}
	BittrexResponseData3 struct {
		Type int64           `json:"Type"`
		Rate decimal.Decimal `json:"Rate"`
		Qty  decimal.Decimal `json:"Quantity"`
	}
	BittrexRequest struct {
		Hub        string   `json:"H"`
		Method     string   `json:"M"`
		Arguments  []string `json:"A"`
		Identifier int64    `json:"I"`
	}
)

func NewBittrex(api, secret string) *Bittrex {
	bittrex := &Bittrex{
		Exchange: NewExchange("bittrex", map[string]string{
			"USDT_BTC": "USDT-BTC",
			"USDT_ETH": "USDT-ETH",
			"USDT_XRP": "USDT-XRP",
			// "USD_XLM":
			"USDT_NEO": "USDT-NEO",
			"USDT_DASH": "USDT-DASH",
			"USDT_XMR": "USDT-XMR",
			// "USD_LSK":
			"BTC_NEM": "BTC-ZEM",
			"BTC_ETH": "BTC-ETH",
			"BTC_XRP": "BTC-XRP",
			"BTC_XLM": "BTC-XLM",
			"BTC_NEO": "BTC-NEO",
			"BTC_DASH": "BTC-DASH",
			"BTC_XMR": "BTC-XMR",
			"BTC_LSK": "BTC-LSK",
                        "ETH_ETC": "ETH-ETC",
                        //"ETH_LTC":  "ETH-LTC",
                        "ETH_OMG": "ETH-OMG",
                        "ETH_GNT": "ETH-GNT",
			"BTC_ZEC": "BTC-ZEC",
			"BTC_LTC": "BTC-LTC",
			"BTC_ETC": "BTC-ETC",
			"BTC_OMG": "BTC-OMG",
			//"BTC_ADA":  "BTC-ADA",
		}),
		CallIndex:    0,
		SubscribeMap: make(map[string]string),
		ResponseMap:  make(map[string]string),
	}
	bittrex.Fee = decimal.New(25, -4)
	return bittrex
}

func (self *Bittrex) negotiate(scheme, address string) (BittrexNegotiationResponse, error) {
	var response BittrexNegotiationResponse
	var negotiationURL = url.URL{Scheme: scheme, Host: address, Path: "/signalr/negotiate"}

	scraper, err := scraper.NewTransport(http.DefaultTransport)
	if err != nil {
		return response, err
	}
	log.Printf("Scraper %s", scraper)
	client := &http.Client{
		Transport: scraper,
	}

	reply, err := client.Get(negotiationURL.String())
	if err != nil {
		return response, err
	}
	defer reply.Body.Close()

	if body, err := ioutil.ReadAll(reply.Body); err != nil {
		return response, err
	} else if err := json.Unmarshal(body, &response); err != nil {
		return response, err
	} else {
		response.Cookie = reply.Request.Header["Cookie"]
		response.UserAgent = reply.Request.Header["User-Agent"]
		return response, nil
	}
}

func (self *Bittrex) connect(address string, params BittrexNegotiationResponse) (*websocket.Conn, error) {
	var connectionParameters = url.Values{}
	connectionParameters.Set("transport", "webSockets")
	connectionParameters.Set("clientProtocol", "1.5")
	connectionParameters.Set("connectionToken", params.ConnectionToken)
	connectionParameters.Set("connectionData", "[{\"name\":\"corehub\"}]")

	var connectionUrl = url.URL{Scheme: "wss", Host: address, Path: "signalr/connect"}
	connectionUrl.RawQuery = connectionParameters.Encode()

	var header = http.Header{
		"User-Agent": params.UserAgent,
		"Cookie":     params.Cookie,
	}

	if conn, _, err := websocket.DefaultDialer.Dial(connectionUrl.String(), header); err != nil {
		return nil, err
	} else {
		return conn, nil
	}
}

func (self *Bittrex) parse(data []byte, ws *websocket.Conn) {
	var res BittrexResponse
	err := json.Unmarshal(data, &res)
	if err != nil {
		log.Printf("Bittrex Error: Could not unmarshal data: %s", err)
		return
	}
	ts := time.Now().UnixNano()
	if res.Identifier == "" {
		var data BittrexResponseData
		for _, val := range res.Data {
			err = json.Unmarshal(val, &data)
			if err != nil {
				log.Printf("Bittrex Error: Could not unmarshal data: %s", err)
				return
			}
			if data.Method == "updateExchangeState" {
				for _, v := range data.Arguments {
					if book, ok := self.OrderBooks[v.Pair]; ok {
						for _, v := range v.Sells {
							book.UpdateAsk(v.Rate, v.Qty, ts)
						}
						for _, v := range v.Buys {
							book.UpdateBid(v.Rate, v.Qty, ts)
						}
					}
				}
			}
		}
		return
	}

	if pair, ok := self.SubscribeMap[res.Identifier]; ok {
		if fmt.Sprintf("%s", res.Result) == "true" {
			log.Printf("Subscribed to %s, asking for orderbook", pair)
			// Ask for initial book
			getBook := BittrexRequest{
				Hub:        "corehub",
				Method:     "queryExchangeState",
				Arguments:  []string{pair},
				Identifier: self.nextResponseIndex(pair), // store a map of ID to pair call
			}
			err := ws.WriteJSON(getBook)
			if err != nil {
				// Probably want to disconnect and reconnect here
				log.Println("Bittrex Error: Could not write to websocket:", err)
			}
		} else {
			log.Printf("Bittrex Error: Failed to Subscribe to %s", pair)
		}
		return
	}
	if pair, ok := self.ResponseMap[res.Identifier]; ok {
		var data BittrexResponseData2
		if err = json.Unmarshal(res.Result, &data); err == nil {
			book, ok := self.OrderBooks[pair]
			if !ok {
				log.Printf("Bittrex Error: Could not find book: %s", pair)
				return
			}
			for _, v := range data.Sells {
				book.UpdateAsk(v.Rate, v.Qty, ts)
			}
			for _, v := range data.Buys {
				book.UpdateBid(v.Rate, v.Qty, ts)
			}
			// Build Book
			self.OrderBooks[pair] = book
			log.Printf("Bittrex Orderbook Received: %s", pair)
		}
		return
	}
}

func (self *Bittrex) nextSubscribeIndex(val string) int64 {
	self.CallIndex++
	key := strconv.FormatInt(self.CallIndex, 10)
	self.SubscribeMap[key] = val
	return self.CallIndex
}
func (self *Bittrex) nextResponseIndex(val string) int64 {
	self.CallIndex++
	key := strconv.FormatInt(self.CallIndex, 10)
	self.ResponseMap[key] = val
	return self.CallIndex
}

func (self *Bittrex) subscribe(ws *websocket.Conn, currency string) {
	if pair, ok := self.PairMap[currency]; ok {
		time.Sleep(time.Second)
		sub := &BittrexRequest{
			Hub:        "corehub",
			Method:     "subscribeToExchangeDeltas",
			Arguments:  []string{pair},
			Identifier: self.nextSubscribeIndex(pair),
		}
		err := ws.WriteJSON(sub)
		if err != nil {
			log.Printf("Bittrex Error: Could not write to websocket: %s", err)
			time.Sleep(10 * time.Second)
			go self.subscribe(ws, currency)
			return
		}
	}
}

func (self *Bittrex) Scrape() {
	params, err := self.negotiate("https", "socket.bittrex.com")
	if err != nil {
		log.Printf("Bittrex Error: Unable to negotiate websocket connection: %s", err)
		time.Sleep(10 * time.Second)
		go self.Scrape()
		return
	}
	ws, err := self.connect("socket.bittrex.com", params)
	if err != nil {
		log.Printf("Bittrex Error: Unable to connect to websocket: %s", err)
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
			log.Println("Bittrex Error: Could not read from websocket:", err)
			time.Sleep(10 * time.Second)
			go self.Scrape()
			return
		}
		self.parse(msg, ws)
	}
}
