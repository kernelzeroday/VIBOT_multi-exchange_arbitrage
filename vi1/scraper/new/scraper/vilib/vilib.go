package vilib

import (
	"fmt"
	"log"
	"strings"

	"github.com/shopspring/decimal"
)

type (
	Pair struct {
		Name         string
		Currency     *Currency
		BaseCurrency *Currency
		Exchanges    map[string]*Exchange
		OrderBooks   map[string]*OrderBook // key = Exchange.Name
		Spreads      map[string]*Spread
	}
	Currency struct {
		Name     string
		Pairs    map[string]*Pair    // key = Pair.Name
		Holdings map[string]*Holding // key = Exchange.Name
	}
	Exchange struct {
		Name, Key, Secret string
		PairMap           map[string]string // key = Pair.Name
		Fee               decimal.Decimal
		OrderBooks        map[string]*OrderBook // key = Inverse PairMap
		Holdings          map[string]*Holding   // key = Pair.Name
		Spreads           map[string]*Spread    // key = Pair.Name
		ErrorChan         chan bool
	}
	Holding struct {
		Name     string
		Exchange *Exchange
		Currency *Currency
		Value    decimal.Decimal
	}
	OrderBook struct {
		Name           string
		Pair           *Pair     `json:"-"`
		PairName       string    `json:"Pair"`
		Exchange       *Exchange `json:"-"`
		ExchangeName   string    `json:"Exchange"`
		LastUpdate     int64
		MinAsk, MaxBid *OrderBookData
		Asks           map[string]*OrderBookData `json:"-"`
		Bids           map[string]*OrderBookData `json:"-"`
		Spreads        map[string]*Spread        `json:"-"`
	}
	OrderBookData struct {
		Key        string
		Price, Qty decimal.Decimal
		Timestamp  int64
	}
	Spread struct {
		Name                                   string
		Pair                                   *Pair      `json:"-"`
		BuyExchange, SellExchange              *Exchange  `json:"-"`
		BuyBook, SellBook                      *OrderBook `json:"-"`
		BuyExchangeName                        string     `json:"BuyFrom"`
		SellExchangeName                       string     `json:"SellTo"`
		BuyFee, SellFee                        decimal.Decimal
		BuyPrice, BuyQty, SellPrice, SellQty   decimal.Decimal
		Value, EMA, EMVAR, Score               decimal.Decimal
		Count, EMARate                         decimal.Decimal
		EMAMaxPos, EMAAge, TimeStart, TimeLast decimal.Decimal
		CurrentMaxValue                        decimal.Decimal `json:"-"`
		CurrentMaxPos                          decimal.Decimal `json:"-"`
		LastUpdate                             int64
		Type                                   string
	}
)

var (
	Pairs      = make(map[string]*Pair)
	Currencies = make(map[string]*Currency)
	Exchanges  = make(map[string]*Exchange)
	Holdings   = make(map[string]*Holding)
	OrderBooks = make(map[string]map[string]*OrderBook)
	Spreads    = make(map[string]*Spread)
)

// NewPair : Expects a string in the format <BASE>_<CURRENCY>
func NewPair(pair string) *Pair {
	// Check if already exists
	if existing, ok := Pairs[pair]; ok {
		return existing
	}

	parts := strings.Split(pair, "_")
	if len(parts) != 2 {
		return nil
	}
	base := parts[0]
	currency := parts[1]
	new := &Pair{
		Name:       fmt.Sprintf("%s_%s", base, currency),
		OrderBooks: make(map[string]*OrderBook),
		Spreads:    make(map[string]*Spread),
	}
	b, ok := Currencies[base]
	if !ok {
		b = NewCurrency(base)
	}
	c, ok := Currencies[currency]
	if !ok {
		c = NewCurrency(currency)
	}
	new.BaseCurrency = b
	new.Currency = c

	b.Pairs[new.Name] = new
	c.Pairs[new.Name] = new
	Pairs[new.Name] = new
	return new
}

func NewCurrency(name string) *Currency {
	new := &Currency{
		Name:     name,
		Pairs:    make(map[string]*Pair),
		Holdings: make(map[string]*Holding),
	}
	Currencies[new.Name] = new
	return new
}

func NewExchange(name string, pairMap map[string]string) *Exchange {
	exchange := &Exchange{
		Name:       name,
		PairMap:    pairMap,
		Fee:        decimal.New(25, -4),
		Holdings:   make(map[string]*Holding),
		OrderBooks: make(map[string]*OrderBook),
		Spreads:    make(map[string]*Spread),
		ErrorChan:  make(chan bool),
	}
	for k, v := range pairMap {
		if pair, ok := Pairs[k]; ok {
			// Create Holdings
			exchange.NewHolding(pair.BaseCurrency)
			exchange.NewHolding(pair.Currency)
			// Create OrderBooks
			exchange.NewOrderBook(v, pair)
		}
	}
	Exchanges[exchange.Name] = exchange
	return exchange
}

func (exchange *Exchange) NewHolding(currency *Currency) {
	holding := &Holding{
		Name: fmt.Sprintf("%s_%s", currency, exchange.Name),
	}
	exchange.Holdings[currency.Name] = holding
	currency.Holdings[exchange.Name] = holding
	Holdings[holding.Name] = holding
}

func (exchange *Exchange) NewOrderBook(key string, pair *Pair) {
	book := &OrderBook{
		Name:         fmt.Sprintf("%s_%s", pair.Name, exchange.Name),
		Pair:         pair,
		PairName:     pair.Name,
		Exchange:     exchange,
		ExchangeName: exchange.Name,
		MinAsk:       new(OrderBookData),
		MaxBid:       new(OrderBookData),
		Asks:         make(map[string]*OrderBookData),
		Bids:         make(map[string]*OrderBookData),
		Spreads:      make(map[string]*Spread),
	}
	exchange.OrderBooks[key] = book
	pair.OrderBooks[exchange.Name] = book
	if _, ok := OrderBooks[pair.Name]; !ok {
		OrderBooks[pair.Name] = make(map[string]*OrderBook)
	}
	OrderBooks[pair.Name][exchange.Name] = book
}

// BuildSpreads - Build spread objects
func BuildSpreads() {
	for pairKey, pair := range Pairs {
		for fromBookKey, fromBook := range OrderBooks[pairKey] {
			for toBookKey, toBook := range OrderBooks[pairKey] {
				name := fmt.Sprintf("%s_%s_%s", pairKey, fromBookKey, toBookKey)
				if _, ok := Spreads[name]; !ok {
					spread := &Spread{
						Name:             name,
						Pair:             pair,
						BuyExchange:      fromBook.Exchange,
						SellExchange:     toBook.Exchange,
						BuyExchangeName:  fromBook.Exchange.Name,
						SellExchangeName: toBook.Exchange.Name,
						BuyFee:           fromBook.Exchange.Fee,
						SellFee:          toBook.Exchange.Fee,
						BuyBook:          fromBook,
						SellBook:         toBook,
					}
					pair.Spreads[name] = spread
					fromBook.Spreads[name] = spread // Subset for updates
					toBook.Spreads[name] = spread   // Subset for updates
					Spreads[name] = spread
					log.Printf("Spread: %s", name)
				}
			}
		}
	}
}
