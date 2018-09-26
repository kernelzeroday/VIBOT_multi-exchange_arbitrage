#!/usr/bin/env
require 'binance_api'

def process (msg)
	puts "msg: #{msg.data}"
end


stream = BinanceAPI::Stream.new(['bnbbtc@aggTrade', 'bnbbtc@trade'], on_message: ->(msg) { put msg.data ; process(msg) })

stream.start

