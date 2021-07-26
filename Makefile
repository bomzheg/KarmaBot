.PHONY: init local_deploy lint test

init:
	virtualenv -q -p python3.9 ./venv3 && . venv3/bin/activate && pip install --upgrade pip && pip install -q -r requirements.txt && pip install -q -r requirements.test.txt

local_deploy: init
	docker-compose up --build -d

lint:
	venv3/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test:
	venv3/bin/pytest

lint_test: lint test