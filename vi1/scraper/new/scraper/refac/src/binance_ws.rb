#!/usr/bin/env ruby
require 'binance'
require 'eventmachine'
require 'sdbm'
require 'json'

SDBM.open '/dev/shm/binance.db' do |db|
	db.clear
end

client = Binance::Client::WebSocket.new
EM.run do
  # Create event handlers
  open    = proc { puts 'connected' }
  message = proc { |e| 
          puts e.data 
          SDBM.open '/dev/shm/binance.db' do |db|
                  name = JSON.load(e.data)['stream']
                  db.store(name, e.data) 
          end
  }
  error   = proc { |e| puts e }
  close   = proc { puts 'closed' }
  File.open("binance.symbols.txt").each do |symbol|
    # Bundle our event handlers into Hash
    methods = { open: open, message: message, error: error, close: close }

    # Pass a symbol and event handler Hash to connect and process events
    client.agg_trade symbol: symbol, methods: methods

    # kline takes an additional named parameter
    client.kline symbol: symbol, interval: '1m', methods: methods

    # As well as partial_book_depth
    client.partial_book_depth symbol: symbol, level: '5', methods: methods

    # Create a custom stream
    # client.single stream: { type: 'aggTrade', symbol: 'XRPETH'}, methods: methods

    # Create multiple streams in one call
    client.multi streams: [ # { type: 'aggTrade', symbol: symbol },
      { type: 'ticker', symbol: symbol }
      # { type: 'kline', symbol: symbol, interval: '1m' },
      # { type: 'depth', symbol: symbol, level: '5' }
    ],
                 methods: methods
  end
end
