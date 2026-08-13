.PHONY: run test lint package docker

run:
	avanegar --reload

test:
	pytest

lint:
	ruff check app tests
	pylint app tests

package:
	python -m build
	twine check dist/*

docker:
	docker build -t avanegar:local .
