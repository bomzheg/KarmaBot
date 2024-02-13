from tortoise import BaseDBAsyncClient

from app.infrastructure.database.models import Chat, ChatSettings


class ChatSettingsRepo:
    def __init__(self, session: BaseDBAsyncClient | None = None):
        self.session = session

    async def get_or_create(self, chat: Chat) -> ChatSettings:
        chat_settings, _ = await ChatSettings.get_or_create(chat=chat, using_db=self.session)
        return chat_settings

    async def update_karma_counting(self, chat_settings: ChatSettings, value: bool):
        if chat_settings.karma_counting == value:
            return

        chat_settings.karma_counting = value
        await chat_settings.save(using_db=self.session)

    async def update_karmic_restriction(self, chat_settings: ChatSettings, value: bool):
        if chat_settings.karmic_restrictions == value:
            return

        chat_settings.karmic_restrictions = value
        await chat_settings.save(using_db=self.session)

    async def update_report_award(self, chat_settings: ChatSettings, value: int):
        if chat_settings.report_karma_award == value:
            return

        chat_settings.report_karma_award = value
        await chat_settings.save(using_db=self.session)
