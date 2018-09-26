def:
	sudo gem install binance binance_api eventmachine websocket-client-simple
	sudo pip3 install bitcoinexchangefh
release: 
	tar Jvpcf /tmp/release.tar.xz --exclude=release.tar.xz --ignore-failed-read ../refac
	mv /tmp/release.tar.xz .
clean:
	rm -rfv release.tar.xz
