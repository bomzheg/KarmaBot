import datetime
import re
import typing

from app.utils.exceptions import TimedeltaParseError, ToLongDuration, InvalidFormatDuration

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


def parse_timedelta(value: str) -> datetime.timedelta:
    match = LINE_PATTERN.match(value)
    if not match:
        raise InvalidFormatDuration("Invalid time format")

    try:
        result = datetime.timedelta()
        for match in PATTERN.finditer(value):
            value, modifier = match.groups()

            result += int(value) * MODIFIERS[modifier]
    except OverflowError:
        raise ToLongDuration("Timedelta value is too large")

    return result


def parse_timedelta_from_text(text_duration: str) -> typing.Optional[datetime.timedelta]:
    if not text_duration:
        return None

    duration = parse_timedelta(text_duration)
    if duration <= datetime.timedelta(seconds=30):
        return datetime.timedelta(seconds=30)
    return duration


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
