from pathlib import Path

from app.config import load_config

load_config(Path(__file__).parent.parent / "config_dist")
