from typing import NamedTuple

from app.models import UserKarma, KarmaEvent, ModeratorEvent


class ResultChangeKarma(NamedTuple):
    user_karma: UserKarma
    abs_change: float
    karma_event: KarmaEvent
    count_auto_restrict: int
    karma_after: float
    moderator_event: ModeratorEvent
