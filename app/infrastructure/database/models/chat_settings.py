from tortoise import fields
from tortoise.models import Model

from app.infrastructure.database.models import Chat


class ChatSettings(Model):
    """
    information about (karma) (user) in (chat)
    """
    id = fields.IntField(pk=True)
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        'models.Chat', related_name='settings')
    karmic_restrictions: bool = fields.BooleanField(default=False)
    karma_counting: bool = fields.BooleanField(null=False, default=True)

    class Meta:
        table = 'chat_settings'

    def __str__(self):
        # noinspection PyUnresolvedReferences
        rez = (
            f'Settings {self.id} of chat: {self.chat_id} '
            f'enable karma {self.karma_counting}'
            f'enable karmic restrictions {self.karmic_restrictions}'
        )
        return rez

    def __repr__(self):
        return f'<ChatSettings id={self.id}>'
