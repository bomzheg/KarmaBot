from app.models.db import Chat, ChatSettings


async def get_chat_settings(chat: Chat) -> ChatSettings:
    chat_settings, _ = await ChatSettings.get_or_create(chat=chat)
    return chat_settings


async def is_enable_karmic_restriction(chat: Chat) -> bool:
    chat_settings = await get_chat_settings(chat=chat)
    return chat_settings.karmic_restrictions


async def disable_karmic_restriction(chat: Chat):
    await change_value_karmic_restriction(chat, False)


async def enable_karmic_restriction(chat: Chat):
    await change_value_karmic_restriction(chat, True)


async def is_enable_karma_counting(chat: Chat) -> bool:
    chat_settings = await get_chat_settings(chat=chat)
    return chat_settings.karma_counting


async def disable_karma_counting(chat: Chat):
    await change_value_karma_counting(chat, False)


async def enable_karma_counting(chat: Chat):
    await change_value_karma_counting(chat, True)


async def change_value_karmic_restriction(chat: Chat, new_value: bool):
    chat_settings = await get_chat_settings(chat=chat)
    if chat_settings.karmic_restrictions == new_value:
        return
    chat_settings.karmic_restrictions = new_value
    await chat_settings.save()


async def change_value_karma_counting(chat: Chat, new_value: bool):
    chat_settings = await get_chat_settings(chat=chat)
    if chat_settings.karma_counting == new_value:
        return
    chat_settings.karma_counting = new_value
    await chat_settings.save()


async def get_settings_card(chat: Chat) -> str:
    chat_settings = await get_chat_settings(chat=chat)
    return render_settings(chat_settings, chat)


def render_settings(chat_settings: ChatSettings, chat: Chat) -> str:
    result = f"Настройки для чата {chat.title} {chat.chat_id}:\n"

    result += f"подсчёт кармы: {chat_settings.karma_counting}. "
    if chat_settings.karma_counting:
        result += "выключить /disable_karma\n"
    else:
        result += "включить /enable_karma\n"
    result += f"кармобаны: {chat_settings.karmic_restrictions}. "
    if chat_settings.karmic_restrictions:
        result += "выключить /disable_karmic_ro\n"
    else:
        result += "включить /enable_karmic_ro\n"
    return result
