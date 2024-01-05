import enum
from dataclasses import dataclass

from app.utils.log import Logger

logger = Logger(__name__)


class DBType(str, enum.Enum):
    postgresql = 'postgresql'
    mysql = 'mysql'
    sqlite = 'sqlite'


@dataclass
class DBConfig:
    type_: DBType | None = None
    user: str | None = None
    password: str | None = None
    name: str | None = None
    host: str | None = None
    port: int | None = None
    path: str | None = None
    driver: str | None = None

    def create_url_config(self):
        url = None
        if self.type_ in (DBType.postgresql, DBType.mysql):
            if not self.driver:
                self.driver = self._get_default_driver()
            if not self.port:
                self.port = self._get_default_port()

            url = (
                f"{self.type_.value}+{self.driver}://"
                f"{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.name}"
            )
        elif self.type_ == DBType.sqlite:
            url = f'{self.type_://self.path}'
        logger.debug(url)
        return url

    def _get_default_driver(self) -> str:
        default_drivers = {
            DBType.postgresql: 'asyncpg',
            DBType.mysql: 'aiomysql'
        }
        return default_drivers.get(self.type_)

    def _get_default_port(self) -> int:
        default_ports = {
            DBType.postgresql: 5432,
            DBType.mysql: 3306
        }
        return default_ports.get(self.type_)
