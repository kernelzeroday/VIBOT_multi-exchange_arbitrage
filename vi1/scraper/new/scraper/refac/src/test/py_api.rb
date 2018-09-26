#!/usr/bin/env ruby
require 'json'
require 'ffi-rzmq'
require 'pp'

begin
	ctx = ZMQ::Context.new
	s = ZMQ::Socket.new(ctx.pointer, ZMQ::SUB)
rescue ContextError => e
	STDERR.puts "Failed to allocate context or socket!"
	raise
end


def assert(rc)
	raise "Last API call failed at #{caller(1)}" unless rc >= 0
end

bind_to = "tcp://127.0.0.1:6001"
assert(s.connect(bind_to))


 
msg = ZMQ::Message.new
msg = ''
assert(s.recv_string(msg))
raise unless msg.to_i == 0
p msg
ob = JSON.load(msg)
pp ob

