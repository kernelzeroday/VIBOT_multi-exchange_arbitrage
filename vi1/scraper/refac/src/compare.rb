#!/usr/bin/env ruby
require 'sdbm'
require 'json'
require 'active_support/core_ext/hash/deep_merge'
require 'net/http'

puts "Locating arbitrage. Please wait"

#binance_snapshot = Net::HTTP.get(URI("https://api.binance.com/api/v1/ticker/24hr"))
#okex_snapshot = Net::HTTP.get(URI("https://www.okex.com/api/v1/ticker.do?symbol="))

binance_symbol_array = []
File.open('binance.symbols.txt').each { |a| binance_symbol_array.push a.chomp.downcase  }
okex_symbol_array = []
File.open('okex.symbols.txt').each { |a| okex_symbol_array.push a.delete('_').chomp }

matches = []
binance_symbol_array.each { |a| matches.push okex_symbol_array.grep(a)[0] unless okex_symbol_array.grep(a).empty? }


binance_symbols_raw = []
File.open('binance.symbols.txt').each { |a| binance_symbols_raw.push a  }
okex_symbols_raw = []
File.open('okex.symbols.txt').each { |a| okex_symbols_raw.push a}



symbol_hash = {}
binance_symbols_raw.each { |a| symbol_hash.update( { a.chomp.downcase => {'binance'=>a.chomp } } ) }
okex_symbols_raw.each { |a| symbol_hash.deep_merge!( { a.delete('_').chomp => {'okex'=>a.chomp } } ) }




while true do
okexobj = {}
SDBM.open '/dev/shm/okex.db' do |db|
	ob = db.to_h
	ob.each { |key,value| okexobj.update({key => JSON.load(value)}) }
end

binanceobj = {}
SDBM.open '/dev/shm/binance.db' do |db|
	ob = db.to_h
	ob.each { |key,value| binanceobj.update({key => JSON.load(value)}) }
end

matches.each { |a|
	begin
		bin = binanceobj["#{a}@ticker"]['data']
		okf = symbol_hash[a]['okex']
		ok = okexobj["ok_sub_spot_#{okf}_ticker"]
		puts "Symbol: #{a} Binance: bid #{bin['b']} ask #{bin['a']}  Okex: bid #{ok['buy']} ask #{ok['sell']} "
		if (bin['b'] > ok['sell'] )
			arb = ( bin['b'].to_f / ok['sell'].to_f )
			puts "*Binance bid larger than Okex ask: #{arb}" 
		end
		if (ok['buy'] > bin['a'])
			arb = ( ok['buy'].to_f / bin['a'].to_f )
			puts "*Okex bid larger than Binance ask: #{arb}"
		end
	rescue => e 
		#puts "Error: #{a} is not in the local cache"
		next
	end
}
sleep 1
end
