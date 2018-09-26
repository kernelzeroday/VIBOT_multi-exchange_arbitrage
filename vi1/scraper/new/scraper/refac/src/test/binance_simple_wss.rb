#!/usr/bin/env ruby
require 'rubygems'
require 'websocket-client-simple'
require 'pp'
require 'json'
require 'sdbm'
require 'net/http'



ws = WebSocket::Client::Simple.connect 'wss://stream.binance.com:9443/ws/!ticker@arr'

btcbnb = WebSocket::Client::Simple.connect 'wss://stream.binance.com:9443/ws/bnbbtc@depth'


orderbook_bnbbtc = JSON.load(Net::HTTP.get(URI("https://www.binance.com/api/v1/depth?symbol=BNBBTC&limit=1000")))

ob = {} 
price = 0



#btcbnb.on :message do |msg|
#	ob = JSON.parse(msg.data)
#	  name = ob['s']
#	  SDBM.open '/dev/shm/binance.db' do |db|
#		  db.store(name, ob.to_json)
#  	  end
#pp ob
#end

ws.on :message do |msg|
  data =  msg.data
  o = JSON.parse(data)
  pp o
end

ws.on :open do
end

ws.on :close do |e|
  p e
  exit 1
end

ws.on :error do |e|
  p e
end

loop do
  ws.send STDIN.gets.strip
end

