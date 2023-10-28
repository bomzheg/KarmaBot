from typing import NamedTuple

from app.infrastructure.database.models import KarmaEvent, ModeratorEvent, UserKarma


class ResultChangeKarma(NamedTuple):
    user_karma: UserKarma
    abs_change: float
    karma_event: KarmaEvent
    count_auto_restrict: int
    karma_after: float
    moderator_event: ModeratorEvent
    was_auto_restricted: bool
