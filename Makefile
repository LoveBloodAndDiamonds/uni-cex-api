clean-macos-trash-stuff:
	find . -name ".DS_Store" -type f -delete

# usage: make make-exchange-from-template EXCHANGE=exchange_name
make-exchange-from-template:
	cp -r tests/_template unicex/$(EXCHANGE)
