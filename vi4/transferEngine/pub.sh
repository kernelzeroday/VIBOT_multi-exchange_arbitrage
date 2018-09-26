for_real(){
return 1
}


echo '{ "action": "transfer",
    "amount": "1",
    "currency": "ETH",
    "from": "poloniex",
    "to": "cex" }'

if for_real;then	

    echo '{"action":"transfer","amount":"1","currency":"ETH","from":"poloniex","to":"cex"}'|mosquitto_pub -t transfers/incoming -s
else:
    printf Not actually doing this\n
fi

