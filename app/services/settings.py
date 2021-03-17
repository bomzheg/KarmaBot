from app.models import Chat, ChatSettings


async def is_enable_karmic_restriction(chat: Chat):
    chat_settings, _ = await ChatSettings.get_or_create(chat=chat)
    return chat_settings.karmic_restrictions


async def disable_karmic_restriction(chat: Chat):
    await change_value_karmic_restriction(chat, False)


async def enable_karmic_restriction(chat: Chat):
    await change_value_karmic_restriction(chat, True)


async def change_value_karmic_restriction(chat: Chat, new_value: bool):
    chat_settings, _ = await ChatSettings.get_or_create(chat=chat)
    if chat_settings.karmic_restrictions == new_value:
        return
    chat_settings.karmic_restrictions = new_value
    await chat_settings.save()
