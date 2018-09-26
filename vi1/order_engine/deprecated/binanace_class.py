class Binance(Exchange):
    def __init__(self, pairs=[]):
        self.api = BinanceAPI(config.binanceKey, config.binanceSecret)
        self.currencyMap = {
            "STR": "XLM",
        }

        thisPairs = {}
        for p in pairs:
            pair = pairInfo.Binance.get(p, False)
            if pair:
                thisPairs[p] = pair
        pairs = thisPairs

        if not pairs:
            raise ValueError("Could not find any pairs")
        inversePairs = {v["name"]: k for k, v in pairs.items()}
        volumeTotal = Decimal()
        
        # Get market volumes
        #tickers = getJSON("https://poloniex.com/public?command=returnTicker")
        #tickers = client.get_klines(symbol=pair, limit=1,interval=Client.KLINE_INTERVAL_30MINUTE)
        tickers = []
        for p in pairs:
            ticker = client.get_klines(symbol=p, limit=1,interval=Client.KLINE_INTERVAL_30MINUTE)
            ticker = ticker[0][5]
            vol = Decimal((ticker).quantize(
                BTC_PRECISION, rounding=ROUND_DOWN
            ))
            
                          
        for k, v in pairs.items():
            
            vol = Decimal(tickers.get(
                v.get("name", False), {})
                .get("baseVolume", 0)
            ).quantize(
                BTC_PRECISION, rounding=ROUND_DOWN
            )
            pairs[k]["volume"] = vol
            volumeTotal += vol
        super().__init__("binance", pairs=pairs, inversePairs=inversePairs, volumeTotal=volumeTotal)
        
    def updateBalance(self, vals):
        # Parse vals
        try:
            res = json.loads(vals, parse_float=Decimal)
        except json.JSONDecodeError:
            # TODO Error decoding json
            pass
        else:
            for currency, data in res.items():
                if isinstance(data, dict):
                    currency = self.currencyMap.get(currency, currency)  # Map for STR -> XLM
                    available = data.get("available", Decimal())
                    pending = data.get("pending", Decimal())
                    super().updateBalance(currency, available, pending)

    def buy(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.order_limit_buy(symbol=pair, quantity=str(qty), price=str(price))
"""
{
  "symbol": "ETHBTC",
  "orderId": 161350753,
  "clientOrderId": "1NkXTEEbfshaVJPnTHbg2E",
  "transactTime": 1528136171616,
  "price": "0.07850000",
  "origQty": "1.00000000",
  "executedQty": "0.00000000",
  "status": "NEW",
  "timeInForce": "GTC",
  "type": "LIMIT",
  "side": "SELL"
}


"""
        except binanceAPI.BinanceApiException as err:
            print("Binance Error Calling API.buy(): %s" % err)
            return False
        else:
            orderID = res.get("clientOrderId", False)
            if not orderID:
                print("Binance Buy Order Placement Failed")
                return False
            # Pass relevant info for tracking and logging via this method's super method (existing in the Exchange class)
            return super().buy(pair, price, qty, kind=kind, orderID=orderID)

    def sell(self, pair, price, qty, kind="Arbitrage"):
        try:
            res = self.api.order_limit_sell(symbol=pair, quantity=str(qty), price=str(price))
            """
            :returns dict
            As above with "type":"sell"
            """
        except binanceAPI.BinanceApiException as err:
            print("Binance Error Calling API.sell(): %s" % err)
            return False
        else:
            orderID = res.get("clientOrderId", False)
            if not orderID:
                print("Binance Sell Order Placement Failed")
                return False
            # Pass relevant info for tracking and logging via this method's super method (existing in the Exchange class)
            return super().sell(pair, price, qty, kind=kind, orderID=orderID)
