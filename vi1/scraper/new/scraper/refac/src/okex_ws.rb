#!/usr/bin/env ruby
require 'rubygems'
require 'websocket-client-simple'
require 'pp'
require 'json'
require 'sdbm'

SDBM.open '/dev/shm/okex.db' do |db|
        db.clear
end



ws = WebSocket::Client::Simple.connect 'wss://real.okex.com:10440/websocket/okexapi'


ob = {} 
price = 0

ws.on :message do |msg|
  data =  msg.data
  o = JSON.parse(data)
  o = o[0]
  p o
  name = o['channel']
  SDBM.open '/dev/shm/okex.db' do |db|
	  db.store(name, o['data'].to_json)
  end
  #if  ( o['data'][0]['symbol'] == "XBTUSD" )
#	xbt = o['data'][0].to_h
#	xbt.keys.each { |a| ob.store(a, xbt[a])  }
#	price = ob['markPrice']
#	#puts "Bitmex XBTUSD:  #{price}"
#	SDBM.open 'dbxbt' do |db|
#		ob.keys.each { |a| db.store(a, ob[a].to_s ) }
#	end
#  end
end

ws.on :open do
	File.open("okex.symbols.txt").each do |symbol| 
		symbol = symbol.chop
		item = "{'event':'addChannel','channel':'ok_sub_spot_#{symbol}_ticker'}" 
		p item
		ws.send item
	#	item = "{'event':'addChannel','channel':'ok_sub_future#{symbol}_ticker'}"
	#	p item
	#	ws.send item
	end
	ws.send "{'event':'addChannel','channel':'ok_sub_futureusd_btc_ticker_this_week'}"
end

ws.on :close do |e|
  p e
  ws = WebSocket::Client::Simple.connect 'wss://real.okex.com:10440/websocket/okexapi'
end

ws.on :error do |e|
  p e
  ws = WebSocket::Client::Simple.connect 'wss://real.okex.com:10440/websocket/okexapi'
end

loop do
  ws.send STDIN.gets.strip
end

