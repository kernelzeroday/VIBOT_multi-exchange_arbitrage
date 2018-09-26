#!/usr/bin/env ruby
while true do

	threads = []

	threads << Thread.new { require ('./src/okex_ws.rb') }
	threads << Thread.new { require ('./src/binance_ws.rb') }
	sleep 900
	#Thread.list.each do |thread|
	#	  thread.exit unless thread == Thread.current
	#end

	puts "cycle"
end

