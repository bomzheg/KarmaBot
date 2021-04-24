# auto restrict when karma less than NEGATIVE_KARMA_TO_RESTRICT
from datetime import timedelta

from app.models.common import TypeRestriction
from app.models.config import AutoRestrictionConfig
from .moderation import FOREVER_RESTRICT_DURATION
from .restriction_plan import RestrictionPlan, RestrictionPlanElem


NEGATIVE_KARMA_TO_RESTRICT = -100
KARMA_AFTER_RESTRICT = -80
RESTRICTIONS_PLAN = RestrictionPlan([
    RestrictionPlanElem(timedelta(days=7), TypeRestriction.karmic_ro),
    RestrictionPlanElem(timedelta(days=30), TypeRestriction.karmic_ro),
    RestrictionPlanElem(FOREVER_RESTRICT_DURATION, TypeRestriction.karmic_ban),
])


def load_karmic_restriction_config() -> AutoRestrictionConfig:
    return AutoRestrictionConfig(
        plan=RESTRICTIONS_PLAN,
        threshold=NEGATIVE_KARMA_TO_RESTRICT,
        after_restriction_karma=KARMA_AFTER_RESTRICT,
    )
