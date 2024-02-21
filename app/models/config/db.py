from dataclasses import dataclass

from app.utils.log import Logger

logger = Logger(__name__)


@dataclass
class DBConfig:
    db_type: str = None
    login: str = None
    password: str = None
    db_name: str = None
    db_host: str = None
    db_port: int = None
    db_path: str = None

    def create_url_config(self):
        if self.db_type == "mysql":
            db_url = (
                f"{self.db_type}://{self.login}:{self.password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        elif self.db_type == "postgres":
            db_url = (
                f"{self.db_type}://{self.login}:{self.password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        elif self.db_type == "sqlite":
            db_url = f"{self.db_type}://{self.db_path}"
        else:
            raise ValueError("DB_TYPE not mysql, sqlite or postgres")
        logger.debug(db_url)
        return db_url
