import asyncio

from app.config.main import load_config
from app.utils.cli import cli

if __name__ == "__main__":
    asyncio.run(cli(load_config()))
