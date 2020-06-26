# Karmabot deploy manual

install docker and docker-compose

install https://github.com/bomzheg/nginx-le

add karmabot.conf to nginx-le bots path (etc/bots)

docker-compose up --build -d

to create tables in database run 
docker-compose exec KarmaBot python initialize.py
