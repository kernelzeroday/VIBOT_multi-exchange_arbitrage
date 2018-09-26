package vilib

import (
	"sort"

	"github.com/shopspring/decimal"
)

func (self *OrderBook) UpdateAsk(decPrice, decQty decimal.Decimal, ts int64) {
	self.LastUpdate = ts
	price := decPrice.String()
	if decQty.Sign() == 0 {
		self.RemoveAsk(price)
		return
	}
	// Add new Ask
	ask := &OrderBookData{
		Key:       price,
		Price:     decPrice,
		Qty:       decQty,
		Timestamp: ts,
	}
	self.Asks[price] = ask
	// Check if new minimum
	if self.MinAsk.Price.Sign() == 0 || ask.Price.LessThan(self.MinAsk.Price) {
		self.SetMinAsk(ask)
	}
}

func (self *OrderBook) UpdateBid(decPrice, decQty decimal.Decimal, ts int64) {
	self.LastUpdate = ts
	price := decPrice.String()
	if decQty.Sign() == 0 {
		self.RemoveBid(price)
		return
	}
	// Add new Bid
	bid := &OrderBookData{
		Key:       price,
		Price:     decPrice,
		Qty:       decQty,
		Timestamp: ts,
	}
	self.Bids[price] = bid
	// Check if new maximum
	if self.MaxBid.Price.Sign() == 0 || bid.Price.GreaterThan(self.MaxBid.Price) {
		self.SetMaxBid(bid)
	}
}

func (self *OrderBook) RemoveAsk(key string) {
	delete(self.Asks, key)
	// Check if the removed ask was the current minimum
	if self.MinAsk == nil || self.MinAsk.Key == key {
		if new := self.GetMinAsk(); new != nil {
			self.SetMinAsk(new)
		}
	}
}
func (self *OrderBook) RemoveBid(key string) {
	delete(self.Bids, key)
	// Check if the removed bid was the current maximum
	if self.MaxBid == nil || self.MaxBid.Key == key {
		if new := self.GetMaxBid(); new != nil {
			self.SetMaxBid(new)
		}
	}
}
func (self *OrderBook) Clear() {
	self.MinAsk = new(OrderBookData)
	self.MaxBid = new(OrderBookData)
	for k := range self.Asks {
		delete(self.Asks, k)
	}
	for k := range self.Bids {
		delete(self.Bids, k)
	}
}
func (self *OrderBook) GetMinAsk() *OrderBookData {
	// If self.Asks is empty return early
	if len(self.Asks) == 0 {
		return nil
	}
	// Initialise slice capacity to match Asks map length for better performance
	s := make([]*OrderBookData, 0, len(self.Asks))
	// Read Asks map into a slice and sort to find minimum
	for _, v := range self.Asks {
		s = append(s, v)
	}
	// Perform ascending sort
	sort.Slice(s, func(i, j int) bool {
		return s[i].Price.LessThan(s[j].Price)
	})
	return self.Asks[s[0].Key]
}

func (self *OrderBook) GetMaxBid() *OrderBookData {
	// If self.Bids is empty return early
	if len(self.Bids) == 0 {
		return nil
	}
	// Initialise slice capacity to match Bids map length for better performance
	s := make([]*OrderBookData, 0, len(self.Bids))
	// Read Bids map into a slice and sort to find maximum
	for _, v := range self.Bids {
		s = append(s, v)
	}
	// Perform descending sort
	sort.Slice(s, func(i, j int) bool {
		return s[i].Price.GreaterThan(s[j].Price)
	})
	return self.Bids[s[0].Key]
}

// These functions can be called directly when not maintaining a full, live orderbook.
// For example, if the Exchange's API supplies current MinAsk and MaxBid separately.
// However, it would be beneficial to have live orderbooks for all exchanges
func (self *OrderBook) SetMinAsk(ask *OrderBookData) {
	*self.MinAsk = *ask // Always update for timestamp
	// log.Printf("%s:%s New MinAsk: %s Qty: %s", self.Exchange.Name, self.Pair.Name, self.MinAsk.Price, self.MinAsk.Qty)
}
func (self *OrderBook) SetMaxBid(bid *OrderBookData) {
	*self.MaxBid = *bid // Always update for timestamp
	// log.Printf("%s:%s New MaxBid: %s Qty: %s", self.Exchange.Name, self.Pair.Name, self.MaxBid.Price, self.MaxBid.Qty)
}
