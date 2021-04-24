from app.config import load_config
from app.models.db.db import generate_schemas

if __name__ == "__main__":
    generate_schemas(load_config().db)
