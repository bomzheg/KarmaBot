from aiogram.utils.text_decorations import html_decoration as hd

from app.infrastructure.database.models import Chat, ChatSettings
from app.infrastructure.database.repo.chat_settings import ChatSettingsRepo


async def disable_karmic_restriction(
    chat_settings: ChatSettings, chat_settings_repo: ChatSettingsRepo
):
    await chat_settings_repo.update_karmic_restriction(chat_settings, False)


async def enable_karmic_restriction(
    chat_settings: ChatSettings, chat_settings_repo: ChatSettingsRepo
):
    await chat_settings_repo.update_karmic_restriction(chat_settings, True)


async def disable_karma_counting(
    chat_settings: ChatSettings, chat_settings_repo: ChatSettingsRepo
):
    await chat_settings_repo.update_karma_counting(chat_settings, False)


async def enable_karma_counting(
    chat_settings: ChatSettings, chat_settings_repo: ChatSettingsRepo
):
    await chat_settings_repo.update_karma_counting(chat_settings, True)


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
