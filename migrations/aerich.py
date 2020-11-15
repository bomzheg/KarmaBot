from app.models.db import get_db_connect_string

TORTOISE_ORM = {
   "connections": {"default": get_db_connect_string()},
   "apps": {
       "models": {
           "models": ["app.models", "aerich.models"],
           "default_connection": "default",
       },
   },
}