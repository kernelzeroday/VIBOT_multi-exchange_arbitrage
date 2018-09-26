#!/usr/bin/env python3.6
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import optparse
import sys
mq_host='172.31.30.189'
mq_port=1883
mq_user='vibot'
mq_pass='NmQ5Nj_3MrAwiNDu'
demo=False
if demo:
    mq_pubtop='transfers/test'
else:
    print('Warning: Live Mode Enabled!')
    mq_pubtop='transfers/incoming'


def reqTransfer(topic=mq_pubtop,mode='interative',fromex=None,toex=None,currency=None,quantity=0.0):
    client = mqtt.Client(client_id="publish_test", clean_session=False)
    client = mqtt.Client('manual_tranfer')
    client.username_pw_set(username='vibot', password='NmQ5Nj_3MrAwiNDu')
    client.connect(mq_host,1883,60)
    if mode == 'interactive':
        try:
            #msg = input(' >> ')
            print('Manual Funds Mangement Client: ')
            currency_ = input('>> Currency: ' )
            amount_ = input('>> Quanity: ')
            from_ = input('>> From Exchange: ')
            to_ = input ('>> To Exchange: ')
        except KeyboardInterrupt:
           client.disconnect()
           sys.exit(0)
        else:
           msg=str('{"action":"transfer","currency":"%s","amount":%s,"from":"%s","to":"%s"}' % (currency_,amount_,from_,to_))
           print('Message: ' + str(msg))
           verify = input('Send? y/n :')
           if verify != 'y':
               sys.exit(1)
           publish.single(mq_pubtop, payload=str(msg), hostname=mq_host, port=mq_port,auth = {'username':mq_user, 'password':mq_pass})
           return
    elif mode == 'cli':
        if currency and quantity and fromex and toex:
            msg=str('{"action":"transfer","currency":"%s","amount":%s,"from":"%s","to":"%s"}' % (currency, quantity,fromex,toex))
            print('Sending Request: ' +msg+'\n')
            publish.single(mq_pubtop, payload=str(msg), hostname=mq_host, port=mq_port,auth = {'username':mq_user, 'password':mq_pass})
        else:
            print('Missing arguments!')
            return False
    client.disconnect();




print('[*] ARGV      :', sys.argv[1:])
parser = optparse.OptionParser()
parser.add_option('-i', '--interactive', 
                  dest="interactive", 
                  action="store_true",
                  default=False,
                  )

parser.add_option('-m', '--mqttd',
                  dest="mqttd",
                  default=False,
                  action="store_true",
                  )
parser.add_option('-c', '--currency', 
                  dest="currency", 
                  default="BTC",
                  )

parser.add_option('-q', '--quantity', 
                  dest="quantity",
                  default="0.0",
                  type="float",
                  )



parser.add_option('-f', '--from', 
                  dest="from_exchange", 
                  type="str",
                  )

parser.add_option('-t', '--to', 
                  dest="to_exchange", 
                  type="str",
                  )

options, remainder = parser.parse_args()

interactive = options.interactive
mqttd = options.mqttd
source = options.from_exchange
dest = options.to_exchange
currency = options.currency
quantity = options.quantity




if interactive:
    reqTransfer(mode='interactive')
else:
    #topic=mq_pubtop,mode='interative',fromex=None,toex=None,currency=None,quantity=0.0
    try:
        reqTransfer(topic=mq_pubtop,mode='cli',fromex=source,toex=dest,currency=currency,quantity=quantity)
    except Exception as err:
        print('Error: '+str(err))
        sys.exit(1)
