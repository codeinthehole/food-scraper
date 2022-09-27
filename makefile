install:
	pip install pip-tools==6.8
	pip-sync

check: black isort flake8 mypy test

mypy:
	mypy .

black:
	black --check .

isort:
	isort --check .

flake8:
	flake8

test:
	pytest -v
