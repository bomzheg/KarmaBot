# KarmaBot run without docker

* install python 3.7+

* create [virtual environment](https://docs.python.org/3/tutorial/venv.html)

* ```pip install -r requirements.txt```

* create .env file with Environment variables or export that variables:
  * KARMA_BOT_TOKEN - api token for tg bot
  * TEST_KARMA_BOT_TOKEN - second api token for tg bot. 
  Used if you need to run test bot for testing some function (commandline param -b)
  * WEBHOOK_HOST, WEBHOOK_PORT, WEBHOOK_PATH, LISTEN_IP, LISTEN_PORT if you need to run with webhook
  * DB_TYPE one of "sqlite", "postgres", "mysql"
  * if you use sqlite you must specify DB_PATH 
  * else you must specify LOGIN_DB, PASSWORD_DB, DB_NAME, DB_HOST, DB_PORT

* ```python -m app```

  * you can specify command lines arguments:
    * -b - using TEST_KARMA_BOT_TOKEN instead KARMA_BOT_TOKEN
    * -p - using polling istead webhook
    * -s - skip updates that accumulated on tg servers
    * -a - autoreload bot when source code changed. Use it only in devlopement mode

* for create tables in database run:

```python initialize.py```

# Karmabot deploy manual with docker:

* install docker and docker-compose

* Optional for webhook:

  * install https://github.com/bomzheg/nginx-le

  * add karmabot.conf to nginx-le bots path (etc/bots)
  
* create .env file with environment variables like in #KarmaBot run without docker
  

```docker-compose up --build -d```

* for  create tables in database run :

```docker-compose exec KarmaBot python initialize.py```


# Secondary setup:
in config.py:
* create chat in telegram and place it chat_id in 
[LOG_CHAT_ID](https://github.com/bomzheg/KarmaBot/blob/d5dcf3f6faead1b1b277143857ea9cdc6a872257/app/config.py#L48)
* on next line you can place that or another chat_id in DUMP_CHAT_ID
* its better to add administrator rights in that chats (generate invite links)
* fill SUPERUSERS and GLOBAL_ADMIN_ID with yours
* you can change PLUS_WORDS, PLUS_TRIGGERS, PLUS_EMOJI, MINUS, MINUS_EMOJI. 
it must be iterable, better is set or frozenset
