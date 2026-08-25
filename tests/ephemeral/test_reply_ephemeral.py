import asyncio
from datetime import datetime

import pytest
from aiogram import types
from aiogram.methods import SendMessage

from app.services.ephemeral import ephemeral_available, reply_ephemeral

AUTHOR_ID = 42


class CapturingBot:
    """Заглушка бота, запоминающая вызванный метод вместо запроса к Telegram."""

    def __init__(self):
        self.called: SendMessage | None = None

    async def __call__(self, method, request_timeout=None):
        self.called = method
        return method


def get_message(chat_type: str) -> types.Message:
    return types.Message(
        message_id=13,
        date=datetime.now(),
        chat=types.Chat(id=-100500, type=chat_type),
        from_user=types.User(id=AUTHOR_ID, is_bot=False, first_name="Sheldon"),
        text="!ro сколько-то",
    )


@pytest.mark.parametrize("chat_type", ["group", "supergroup"])
def test_ephemeral_available_in_groups(chat_type: str):
    assert ephemeral_available(get_message(chat_type).chat)


@pytest.mark.parametrize("chat_type", ["private", "channel"])
def test_ephemeral_not_available_outside_groups(chat_type: str):
    assert not ephemeral_available(get_message(chat_type).chat)


@pytest.mark.parametrize("chat_type", ["group", "supergroup"])
def test_reply_ephemeral_addresses_message_author(chat_type: str):
    bot = CapturingBot()
    message = get_message(chat_type).as_(bot)

    asyncio.run(reply_ephemeral(message, "Не могу распознать время."))

    assert isinstance(bot.called, SendMessage)
    assert bot.called.receiver_user_id == AUTHOR_ID
    assert bot.called.chat_id == message.chat.id
    assert bot.called.reply_parameters.message_id == message.message_id


def test_reply_ephemeral_falls_back_to_plain_reply_in_private():
    bot = CapturingBot()
    message = get_message("private").as_(bot)

    asyncio.run(reply_ephemeral(message, "Только в группах."))

    assert isinstance(bot.called, SendMessage)
    assert bot.called.receiver_user_id is None
    assert bot.called.reply_parameters.message_id == message.message_id
