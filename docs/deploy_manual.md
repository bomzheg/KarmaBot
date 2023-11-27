# KarmaBot run without docker

* Install python 3.9+

* Create [virtual environment](https://docs.python.org/3/tutorial/venv.html) and activate it

* Install requirements: ```python -m pip install -r requirements.txt```

* Check out config samples in `config_dist` directory.
  You may want to copy that dir and rename it to `config`, this will make the steps below easier.

* Create `config/.env` file with environment variables or export these variables:
  * `KARMA_BOT_TOKEN` - api token for tg bot
  * fill `WEBHOOK_HOST`, `WEBHOOK_PORT`, `WEBHOOK_PATH`, `LISTEN_IP`, `LISTEN_PORT` if you need to run with webhook
  * `DB_TYPE` one of "sqlite", "postgres" or "mysql"
  * if you are using sqlite you have to specify `DB_PATH`
  * in other case you need to specify `DB_LOGIN`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST` (can skip, default is localhost),
    `DB_PORT` (can skip, default is default port for a current db (example: 5432 for postgres))
* Note: you need to install asyncpg in order to use app with postgresql database.
* Create `config/bot-config.yaml` and fill it with variables:
  * `dump_chat_id` and `log_chat_id` - these will be used to send database dumps and bot logs respectively.
  * `superusers` - list of telegram user ids to become bots superusers.
  * `storage` section - storage to be used. Check out example in `config_dist`.

* Start bot with polling: ```python -m app -p```

  * possible command line arguments:
    * -p - using polling instead webhook
    * -s - skip updates that accumulated on tg servers

* To create tables in database run script:\
```PYTHONPATH=. python migrations/01_initialize.py```
* for run concrete sql migration:\
```PYTHONPATH=. python migrations/migrate.py 05_add_report_table.sql```

# Karmabot deploy manual with a docker:

* install docker and docker-compose

* Optional for webhook:

  * install https://github.com/bomzheg/nginx-le

  * add karmabot.conf to nginx-le bots path (etc/bots)

* create .env file with environment variables like in #KarmaBot run without docker

```docker-compose up --build -d```

* to  create tables in database run :\
```docker-compose exec karmabot  bash -c "PYTHONPATH=. /opt/venv/bin/python /migrations/01_initialize.py"```

* for run sql migration: \
```docker-compose exec karmabot  bash -c "PYTHONPATH=. /opt/venv/bin/python /migrations/migrate.py 05_add_report_table.sql"```

# The secondary setup:
* To generate invite links, the bot must have administrator rights
* you can change `PLUS_WORDS`, `PLUS_TRIGGERS`, `PLUS_EMOJI`, `MINUS_EMOJI` in `app/config/karmic_triggers.py`.
They must be iterable, better is set or frozenset.
