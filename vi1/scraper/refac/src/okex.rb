#!/usr/bin/env ruby
require 'sdbm'
require 'pp'
require 'json'

array = []
SDBM.open '/dev/shm/okex.db' do |db|
	ob = db.to_h
	ob.each { |key,value| array << { key => JSON.load(value)  } }
	pp array

end
