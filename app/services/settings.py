from aiogram.utils.text_decorations import html_decoration as hd

from app.infrastructure.database.models import Chat, ChatSettings


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


async def is_karma_enabled(chat: Chat) -> bool:
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
    result = f"Настройки для чата {chat.title} {chat.chat_id}:\n\n"

    result += f"Подсчёт кармы: {chat_settings.karma_counting}.\n"
    if chat_settings.karma_counting:
        result += "Выключить - /disable_karma\n"
    else:
        result += "Включить - /enable_karma\n"

    result += f"\nКармобаны: {chat_settings.karmic_restrictions}.\n"
    if chat_settings.karmic_restrictions:
        result += "Выключить - /disable_karmic_ro\n"
    else:
        result += "Включить - /enable_karmic_ro\n"

    result += (
        f"\nНаграда за репорт: +{chat_settings.report_karma_award} кармы.\n"
        f"Изменить - {hd.code(hd.quote('/set_report_reward <число>'))}\n"
        f"Выключить - {hd.code('/set_report_reward 0')}\n"
    )
    if not chat_settings.karma_counting:
        result += "Чтобы награды за репорт работали, необходимо включить подсчёт кармы в чате.\n\n"

    return result


async def update_report_reward(chat_settings: ChatSettings, value: int):
    if chat_settings.report_karma_award == value:
        return
    chat_settings.report_karma_award = value
    await chat_settings.save()
