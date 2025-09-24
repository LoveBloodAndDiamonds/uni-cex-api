clean-macos-trash-stuff:
	find . -name ".DS_Store" -type f -delete

pypi-build:
	python -m build ; rm -rf unicex.egg-info

pypi-publish:
	python -m twine upload dist/* ; rm ; rm -rf dist

pypi-build-and-publish:
	python -m build ; rm -rf unicex.egg-info ; python -m twine upload dist/* ; rm ; rm -rf dist

git-merge-to-main:
	# Переключаемся на ветку main
	git checkout main

	# Подтягиваем последние изменения из удалённого репозитория
	git pull origin main

	# Сливаем ветку dev в main
	git merge dev

	# Отправляем обновлённую ветку main на удалённый репозиторий
	git push origin main
