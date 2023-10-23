import typing
from dataclasses import dataclass

from app.config.restriction_plan import RestrictionPlan, RestrictionPlanElem

if typing.TYPE_CHECKING:
    from app.infrastructure.database.models import User


@dataclass
class AutoRestrictionConfig:
    plan: RestrictionPlan
    threshold: int
    after_restriction_karma: int

    @property
    def comment_for_auto_restrict(self):
        return f"Карма ниже {self.threshold}"

    def need_restrict(self, karma: float):
        return karma <= self.threshold

    def get_early_restriction_printable_duration(self, count: int) -> str:
        return self.plan.get_early_restriction_printable_duration(count)

    def get_next_restriction(self, count: int) -> RestrictionPlanElem:
        return self.plan.get_next_restriction(count)

    def get_next_restriction_printable_duration(self, count: int) -> str:
        return self.plan.get_next_restriction_printable_duration(count)

    def it_was_last_restriction(self, count: int) -> bool:
        return self.plan.it_was_last_restriction(count)

    def next_will_be_last_restriction(self, count: int) -> bool:
        return self.plan.next_will_be_last_restriction(count)

    def render_auto_restriction(self, user: 'User', count_auto_restrict: int):
        if count_auto_restrict <= 0:
            return ""
        text = "{target}, Уровень вашей кармы стал ниже {negative_limit}.\n".format(
            target=user.mention_link,
            negative_limit=self.threshold,
        )
        if self.plan.it_was_last_restriction(count_auto_restrict):
            text += "Это был последний разрешённый раз. Теперь вы получаете вечное наказание."
        else:
            text += (
                "За это вы наказаны на срок {duration}\n"
                "Вам установлена карма {karma_after}. "
                "Если Ваша карма снова достигнет {threshold} "
                "Ваше наказание будет строже.".format(
                    duration=self.plan.get_early_restriction_printable_duration(count_auto_restrict),
                    karma_after=self.after_restriction_karma,
                    threshold=self.threshold,
                )
            )
        return text

    def render_negative_karma_notification(self, user: 'User', count_auto_restrict: int):
        if self.next_will_be_last_restriction(count_auto_restrict):
            template = (
                "Внимание {username}!\nУ Вас отрицательная карма. "
                "Как только она снова достигнет {threshold} "
                "Вы больше никогда не сможете писать в чат."
            )
            return template.format(
                username=user.mention_link,
                threshold=self.threshold,
            )
        template = (
            "Внимание {username}!\nУ Вас отрицательная карма. "
            "Как только она достигнет {threshold} "
            "Вы не сможете писать в чат на протяжении {duration}"
        )
        return template.format(
            username=user.mention_link,
            threshold=self.threshold,
            duration=self.plan.get_next_restriction_printable_duration(count_auto_restrict),
        )
