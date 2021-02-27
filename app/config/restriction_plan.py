import typing
from datetime import timedelta

from app.models.common import TypeRestriction
from app.utils.timedelta_functions import format_timedelta


class RestrictionPlanElem(typing.NamedTuple):
    duration: timedelta
    type_restriction: TypeRestriction

    @property
    def printable_duration(self):
        return format_timedelta(self.duration)


NO_RESTRICTION = RestrictionPlanElem(timedelta(0), TypeRestriction.no_one)


class RestrictionPlan:
    plan: list[RestrictionPlanElem]

    def __init__(self, plan: list[RestrictionPlanElem]):
        self.plan = plan

    def get_early_restriction(self, count: int) -> RestrictionPlanElem:
        if count <= 0:
            return NO_RESTRICTION
        if self.it_was_last_restriction(count):
            return self.plan[-1]
        return self.plan[count]

    def get_early_restriction_printable_duration(self, count: int) -> str:
        return self.get_early_restriction(count).printable_duration

    def get_next_restriction(self, count: int) -> RestrictionPlanElem:
        if self.it_was_last_restriction(count):
            return self.plan[-1]
        return self.plan[count]

    def get_next_restriction_printable_duration(self, count: int) -> str:
        return self.get_next_restriction(count).printable_duration

    def it_was_last_restriction(self, count: int) -> bool:
        return count >= len(self.plan)
