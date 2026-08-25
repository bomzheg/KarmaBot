"""
Отправка эфемерных сообщений (Bot API 10.2).

Эфемерное сообщение доставляется только одному пользователю группы и пропадает
само, поэтому оно хорошо подходит для служебных ответов модераторских команд:
жалоб на нехватку прав, ошибок разбора аргументов и прочего шума, который
не должен оставаться в истории чата.
"""

from typing import Any

from aiogram import types
from aiogram.enums import ChatType

#: Эфемерные сообщения поддерживаются только в группах и супергруппах.
EPHEMERAL_CHAT_TYPES = frozenset((ChatType.GROUP, ChatType.SUPERGROUP))


def ephemeral_available(chat: types.Chat) -> bool:
    """Можно ли отправить эфемерное сообщение в этот чат."""
    return chat.type in EPHEMERAL_CHAT_TYPES


async def reply_ephemeral(message: types.Message, text: str, **kwargs: Any) -> types.Message:
    """
    Ответить на сообщение эфемерным сообщением, видимым только его автору.

    В чатах, где эфемерные сообщения не поддерживаются (например, в личке),
    отправляется обычный ответ.
    """
    if not ephemeral_available(message.chat) or message.from_user is None:
        return await message.reply(text, **kwargs)

    return await message.answer(
        text,
        reply_parameters=message.as_reply_parameters(),
        receiver_user_id=message.from_user.id,
        **kwargs,
    )
