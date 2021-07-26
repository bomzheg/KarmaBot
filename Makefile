.PHONY: init local_deploy

init:
	virtualenv -q -p python3.9 ./venv3 && . venv3/bin/activate && pip install --upgrade pip && pip install -q -r requirements.txt

local_deploy: init
	docker-compose up --build -d

