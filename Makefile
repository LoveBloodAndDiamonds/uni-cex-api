clean-macos-trash-stuff:
	find . -name ".DS_Store" -type f -delete

pypi-build:
	python -m build ; rm -rf unicex.egg-info

pypi-publish:
	python -m twine upload dist/* ; rm ; rm -rf dist

pypi-build-and-publish:
	python -m build ; rm -rf unicex.egg-info ; python -m twine upload dist/* ; rm ; rm -rf dist

# usage: make make-exchange-from-template EXCHANGE=exchange_name
make-exchange-from-template:
	cp -r tests/_template unicex/$(EXCHANGE)
