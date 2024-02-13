import typing
from datetime import timedelta
from random import choice

CORRECT_SIMPLE = [
    ("3s", timedelta(seconds=3)),
    ("5m", timedelta(minutes=5)),
    ("7h", timedelta(hours=7)),
    ("9d", timedelta(days=9)),
    ("2w", timedelta(weeks=2)),
    ("1y", timedelta(days=365)),
]
CORRECT_TUPLE_TYPE = typing.Tuple[str, timedelta]


def get_difficult_correct(
    count: int = 10, count_in_one_up_to: int = 3
) -> typing.List[CORRECT_TUPLE_TYPE]:
    return [get_many_correct(i) for _ in range(count) for i in range(2, count_in_one_up_to)]


def get_many_correct(count: int = 2) -> CORRECT_TUPLE_TYPE:
    assert count >= 2, "count must be more that 2"
    parts = [choice(CORRECT_SIMPLE) for _ in range(count)]
    rez = parts[0]
    for part in parts[1:]:
        rez = calculate_pair_correct(rez, part)
    return rez


def calculate_pair_correct(one: CORRECT_TUPLE_TYPE, two: CORRECT_TUPLE_TYPE) -> CORRECT_TUPLE_TYPE:
    return one[0] + two[0], one[1] + two[1]
