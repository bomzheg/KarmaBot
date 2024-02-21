from app.utils.timedelta_functions import parse_timedelta

from .fixtures import CORRECT_SIMPLE, get_difficult_correct


def test_parse_correct():
    for text, correct_rez in CORRECT_SIMPLE:
        assert parse_timedelta(text) == correct_rez

    for text, correct_rez in get_difficult_correct():
        assert parse_timedelta(text) == correct_rez
