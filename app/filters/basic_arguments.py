from typing import Any

from aiogram.filters import CommandObject
from aiogram.types import Message


def single_int(_: Message, command: CommandObject) -> dict[str, Any]:
    try:
        return {"value": int(float(command.args))}
    except (ValueError, TypeError):
        return {}


def single_non_negative_int(_: Message, command: CommandObject) -> dict[str, Any]:
    value = single_int(_, command).get("value", -1)
    return {"value": value} if value >= 0 else {}
