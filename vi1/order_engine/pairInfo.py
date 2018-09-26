#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from decimal import *
PAIR_ARR = ["BTC_XRP", "BTC_ETH", "BTC_DASH", "BTC_ZEC", "BTC_XLM", "BTC_LTC", "BTC_ETC", "BTC_XMR", "BTC_OMG", "BTC_LSK", "BTC_XEM", "BTC_GNT", "ETH_ZEC", "ETH_ETC", "ETH_GNT", "ETH_OMG", "ETH_ZRX", "BTC_REP", "BTC_RDD", "BTC_SC", "BTC_ZRX"]

Okex = {
    "BTC_REP": {
        "name": "BTC-REP",
        "base": "BTC",
        "quote": "REP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_RDD": {
        "name": "BTC-RDD",
        "base": "BTC",
        "quote": "RDD",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('1000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),

},
    "BTC_ZRX": {
        "name": "BTC-ZRX",
        "base": "BTC",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('50'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "BTC_XRP":  {
        "name": "BTC-XRP",
        "base": "BTC",
        "quote": "XRP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_ETH":  {
        "name": "BTC-ETH",
        "base": "BTC",
        "quote": "ETH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.0005'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_DASH": {
        "name": "BTC-DASH",
        "base": "BTC",
        "quote": "DASH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.015'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ZEC":  {
        "name": "BTC-ZEC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "BTC-XLM",
        "base": "BTC",
        "quote": "XLM",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_LTC": {
        "name": "BTC-LTC",
        "base": "BTC",
        "quote": "LTC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ETC": {
        "name": "BTC-ETC",
        "base": "BTC",
        "quote": "ETC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.016'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XMR": {
        "name": "BTC-XMR",
        "base": "BTC",
        "quote": "XMR",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XEM": {
        "name": "BTC-XEM",
        "base": "BTC",
        "quote": "XEM",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('15'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.1'),
    },

    "BTC_LSK": {
        "name": "BTC-LSK",
        "base": "BTC",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('1'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_SC": {
        "name": "BTC-SC",
        "base": "BTC",
        "quote": "SC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('50'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "ETH_ETC":  {
        "name": "ETH-ETC",
        "base": "ETC",
        "quote": "ETC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.01500000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LTC":  {
        "name": "ETH-LTC",
        "base": "ETC",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.02500000'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_OMG":  {
        "name": "ETH-OMG",
        "base": "ETC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('0.025'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.0001'),
    },
    "ETH_GNT":  {
        "name": "ETH-GNT",
        "base": "ETC",
        "quote": "GNT",
        "minType": "ccxt",
        "minQty": Decimal('5.0'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LSK":  {
        "name": "ETH-LSK",
        "base": "ETH",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.0001'),
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "ETH_ZRX":  {
        "name": "ETH_ZRX",
        "base": "ETH",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.15'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_OMG":  {
        "name": "BTC-OMG",
        "base": "BTC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('1.0'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('1'),
    },


    "USD_BTC":  {
        "name": "USDT-BTC",
        "base": "USDT",
        "quote": "BTC",
        "minType": "ccxt",
        "minQty": Decimal('0.0001'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETH":  {
        "name": "USDT-ETH",
        "base": "USDT",
        "quote": "ETH",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ZEC":  {
        "name": "USDT-ZEC",
        "base": "USDT",
        "quote": "ZEC",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_DASH":  {
        "name": "USDT-DASH",
        "base": "USDT",
        "quote": "DASH",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },


    "USD_LTC":  {
        "name": "USDT-LTC",
        "base": "USDT",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_XMR":  {
        "name": "USDT-XMR",
        "base": "USDT",
        "quote": "XMR",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETC":  {
        "name": "USDT-ETC",
        "base": "USDT",
        "quote": "ETC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

}

Bittrex = {
    "BTC_REP": {
        "name": "BTC-REP",
        "base": "BTC",
        "quote": "REP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_RDD": {
        "name": "BTC-RDD",
        "base": "BTC",
        "quote": "RDD",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('1000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),

},
    "BTC_ZRX": {
        "name": "BTC-ZRX",
        "base": "BTC",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('50'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "BTC_XRP":  {
        "name": "BTC-XRP",
        "base": "BTC",
        "quote": "XRP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_ETH":  {
        "name": "BTC-ETH",
        "base": "BTC",
        "quote": "ETH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.0005'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_DASH": {
        "name": "BTC-DASH",
        "base": "BTC",
        "quote": "DASH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.015'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ZEC":  {
        "name": "BTC-ZEC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "BTC-XLM",
        "base": "BTC",
        "quote": "XLM",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_LTC": {
        "name": "BTC-LTC",
        "base": "BTC",
        "quote": "LTC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ETC": {
        "name": "BTC-ETC",
        "base": "BTC",
        "quote": "ETC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.016'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XMR": {
        "name": "BTC-XMR",
        "base": "BTC",
        "quote": "XMR",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XEM": {
        "name": "BTC-XEM",
        "base": "BTC",
        "quote": "XEM",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('15'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.1'),
    },

    "BTC_LSK": {
        "name": "BTC-LSK",
        "base": "BTC",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('1'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_SC": {
        "name": "BTC-SC",
        "base": "BTC",
        "quote": "SC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('50'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "ETH_ETC":  {
        "name": "ETH-ETC",
        "base": "ETC",
        "quote": "ETC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.01500000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LTC":  {
        "name": "ETH-LTC",
        "base": "ETC",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.02500000'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_OMG":  {
        "name": "ETH-OMG",
        "base": "ETC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('0.025'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.0001'),
    },
    "ETH_GNT":  {
        "name": "ETH-GNT",
        "base": "ETC",
        "quote": "GNT",
        "minType": "ccxt",
        "minQty": Decimal('5.0'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LSK":  {
        "name": "ETH-LSK",
        "base": "ETH",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.0001'),
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "ETH_ZRX":  {
        "name": "ETH_ZRX",
        "base": "ETH",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.15'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_OMG":  {
        "name": "BTC-OMG",
        "base": "BTC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('1.0'),
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('1'),
    },


    "USD_BTC":  {
        "name": "USDT-BTC",
        "base": "USDT",
        "quote": "BTC",
        "minType": "ccxt",
        "minQty": Decimal('0.0001'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETH":  {
        "name": "USDT-ETH",
        "base": "USDT",
        "quote": "ETH",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ZEC":  {
        "name": "USDT-ZEC",
        "base": "USDT",
        "quote": "ZEC",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_DASH":  {
        "name": "USDT-DASH",
        "base": "USDT",
        "quote": "DASH",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },


    "USD_LTC":  {
        "name": "USDT-LTC",
        "base": "USDT",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_XMR":  {
        "name": "USDT-XMR",
        "base": "USDT",
        "quote": "XMR",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETC":  {
        "name": "USDT-ETC",
        "base": "USDT",
        "quote": "ETC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

}

Cex = {
    "BTC_XRP":  {
        "name": "XRP/BTC",
        "base": "BTC",
        "quote": "XRP",
        "minType": "ccxt",
        "minQty": Decimal('40.00'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_ETH":  {
        "name": "ETH/BTC",
        "base": "BTC",
        "quote": "ETH",
        "minType": "ccxt",
        "minQty": Decimal('0.025'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_DASH": {
        "name": "DASH/BTC",
        "base": "BTC",
        "quote": "DASH",
        "minType": "ccxt",
        "minQty": Decimal('0.015'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ZEC":  {
        "name": "ZEC/BTC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "ccxt",
        "minQty": Decimal('0.03'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "XLM/BTC",
        "base": "BTC",
        "quote": "XLM",
        "minType": "ccxt",
        "minQty": Decimal('70.00'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    
}

Poloniex = {
   "BTC_ZRX": {
        "name": "BTC_ZRX",
        "base": "BTC",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        #"minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "BTC_SC": {
        "name": "BTC_SC",
        "base": "BTC",
        "quote": "SC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        #"minQty": Decimal('1'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},
   "BTC_REP": {
        "name": "BTC_REP",
        "base": "BTC",
        "quote": "REP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.02'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_RDD": {
        "name": "BTC_RDD",
        "base": "BTC",
        "quote": "RDD",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('100'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
},
    "BTC_XRP":  {
        "name": "BTC_XRP",
        "base": "BTC",
        "quote": "XRP",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_ETH":  {
        "name": "BTC_ETH",
        "base": "BTC",
        "quote": "ETH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_DASH": {
        "name": "BTC_DASH",
        "base": "BTC",
        "quote": "DASH",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.0001'),
    },
    "BTC_ZEC":  {
        "name": "BTC_ZEC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "BTC_STR",
        "base": "BTC",
        "quote": "XLM",
        "quoteAlt": "STR",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XEM": {
        "name": "BTC_XEM",
        "base": "BTC",
        "quote": "XEM",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('10'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.1'),
    },

    "BTC_LTC": {
        "name": "BTC_LTC",
        "base": "BTC",
        "quote": "LTC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_ETC": {
        "name": "BTC_ETC",
        "base": "BTC",
        "quote": "ETC",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XMR": {
        "name": "BTC_XMR",
        "base": "BTC",
        "quote": "XMR",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_LSK": {
        "name": "BTC_LSK",
        "base": "BTC",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_ETC":  {
        "name": "ETH_ETC",
        "base": "ETC",
        "quote": "ETC",
        "minType": "ccxt",
        "minQty": Decimal('0.01500000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LTC":  {
        "name": "ETH_LTC",
        "base": "ETC",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.02500000'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_OMG":  {
        "name": "ETH_OMG",
        "base": "ETC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('0.025'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_GNT":  {
        "name": "ETH_GNT",
        "base": "ETC",
        "quote": "GNT",
        "minType": "ccxt",
        "minQty": Decimal('5.0'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LSK":  {
        "name": "ETH_LSK",
        "base": "ETH",
        "quote": "LSK",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "ETH_ZRX":  {
        "name": "ETH_ZRX",
        "base": "ETH",
        "quote": "ZRX",
        "minType": "ccxt",
        "minVal": Decimal('0.001'),
        "minQty": Decimal('0.15'),
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},

    "BTC_OMG":  {
        "name": "BTC-OMG",
        "base": "BTC",
        "quote": "OMG",
        "minType": "ccxt",
        "minQty": Decimal('1.0'),
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_BTC":  {
        "name": "USDT_BTC",
        "base": "USDT",
        "quote": "BTC",
        "minType": "ccxt",
        "minQty": Decimal('0.0001'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETH":  {
        "name": "USDT_ETH",
        "base": "USDT",
        "quote": "ETH",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ZEC":  {
        "name": "USDT_ZEC",
        "base": "USDT",
        "quote": "ZEC",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_DASH":  {
        "name": "USDT_DASH",
        "base": "USDT",
        "quote": "DASH",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },


    "USD_LTC":  {
        "name": "USDT_LTC",
        "base": "USDT",
        "quote": "LTC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_XMR":  {
        "name": "USDT_XMR",
        "base": "USDT",
        "quote": "XMR",
        "minType": "ccxt",
        "minQty": Decimal('0.005'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },

    "USD_ETC":  {
        "name": "USDT_ETC",
        "base": "USDT",
        "quote": "ETC",
        "minType": "ccxt",
        "minQty": Decimal('0.01'),
        "pricePrecision": Decimal('0.000000001'),
        "qtyPrecision": Decimal('1'),
    },






}

Binance = {
    "BTC_REP": {
        "name": "BTC-REP",
        "base": "BTC",
        "quote": "REP",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_RDD": {
        "name": "BTC-RDD",
        "base": "BTC",
        "quote": "RDD",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),

},
    "BTC_ZRX": {
        "name": "BTC-ZRX",
        "base": "BTC",
        "quote": "ZRX",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "BTC_XRP":  {
        "name": "BTC-XRP",
        "base": "BTC",
        "quote": "XRP",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_ETH":  {
        "name": "BTC-ETH",
        "base": "BTC",
        "quote": "ETH",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_DASH": {
        "name": "BTC-DASH",
        "base": "BTC",
        "quote": "DASH",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ZEC":  {
        "name": "BTC-ZEC",
        "base": "BTC",
        "quote": "ZEC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('0.01'),
    },
    "BTC_XLM":  {
        "name": "BTC-XLM",
        "base": "BTC",
        "quote": "XLM",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_LTC": {
        "name": "BTC-LTC",
        "base": "BTC",
        "quote": "LTC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.0000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_ETC": {
        "name": "BTC-ETC",
        "base": "BTC",
        "quote": "ETC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XMR": {
        "name": "BTC-XMR",
        "base": "BTC",
        "quote": "XMR",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "BTC_XEM": {
        "name": "BTC-XEM",
        "base": "BTC",
        "quote": "XEM",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.1'),
    },

    "BTC_LSK": {
        "name": "BTC-LSK",
        "base": "BTC",
        "quote": "LSK",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "BTC_SC": {
        "name": "BTC-SC",
        "base": "BTC",
        "quote": "SC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.01'),
},

    "ETH_ETC":  {
        "name": "ETH-ETC",
        "base": "ETC",
        "quote": "ETC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LTC":  {
        "name": "ETH-LTC",
        "base": "ETC",
        "quote": "LTC",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_OMG":  {
        "name": "ETH-OMG",
        "base": "ETC",
        "quote": "OMG",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.0001'),
    },
    "ETH_GNT":  {
        "name": "ETH-GNT",
        "base": "ETC",
        "quote": "GNT",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('1'),
    },
    "ETH_LSK":  {
        "name": "ETH-LSK",
        "base": "ETH",
        "quote": "LSK",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
    },
    "ETH_ZRX":  {
        "name": "ETH_ZRX",
        "base": "ETH",
        "quote": "ZRX",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.00000001'),
        "qtyPrecision": Decimal('0.001'),
},
    "BTC_OMG":  {
        "name": "BTC-OMG",
        "base": "BTC",
        "quote": "OMG",
        "minType": "ccxt",
        "pricePrecision": Decimal('0.000001'),
        "qtyPrecision": Decimal('1'),
    },


}


