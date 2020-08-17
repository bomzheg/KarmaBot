import datetime
import re
import typing

from aiogram import types

MODIFIERS = {
    "y": datetime.timedelta(days=365),  # простим один день если кому-то попадётся високосный
    "w": datetime.timedelta(weeks=1),
    "d": datetime.timedelta(days=1),
    "h": datetime.timedelta(hours=1),
    "m": datetime.timedelta(minutes=1),
    "s": datetime.timedelta(seconds=1),
}
ALL_MODIFIER = "".join(MODIFIERS.keys())
PATTERN = re.compile(rf"(?P<value>\d+)(?P<modifier>[{ALL_MODIFIER}])")
LINE_PATTERN = re.compile(rf"^(\d+[{ALL_MODIFIER}])+$")
DEFAULT_TIME_DELTA = datetime.timedelta(hours=1)


class TimedeltaParseError(Exception):
    pass


def parse_timedelta(value: str) -> datetime.timedelta:
    match = LINE_PATTERN.match(value)
    if not match:
        raise TimedeltaParseError("Invalid time format")

    try:
        result = datetime.timedelta()
        for match in PATTERN.finditer(value):
            value, modifier = match.groups()

            result += int(value) * MODIFIERS[modifier]
    except OverflowError:
        raise TimedeltaParseError("Timedelta value is too large")

    return result


async def parse_timedelta_from_message(
    message: types.Message
) -> typing.Optional[datetime.timedelta]:
    _, *args = message.text.split()

    if args:  # Parse custom duration
        try:
            duration = parse_timedelta(args[0])
        except TimedeltaParseError:
            await message.reply("Failed to parse duration")
            return
        if duration <= datetime.timedelta(seconds=30):
            return datetime.timedelta(seconds=30)
        return duration
    else:
        return DEFAULT_TIME_DELTA


def format_timedelta(td: datetime.timedelta) -> str:
    rez = ""
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    if days == 0 and td.seconds == 0:
        return "0 сек."
    if days > 0:
        rez += f"{days} дн. "
    if hours > 0:
        rez += f"{hours} ч. "
    if minutes > 0:
        rez += f"{minutes} мин. "
    if seconds > 0:
        rez += f"{seconds} сек. "
    return rez.strip()
