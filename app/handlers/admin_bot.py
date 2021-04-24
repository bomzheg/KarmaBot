import io
import json

from aiogram import types

from app.misc import bot, dp
from app.models.config import Config
from app.models.db import (
    Chat,
    User,
    UserKarma,
)
from app.utils.log import Logger
from app.utils.send_text_file import send_log_files

logger = Logger(__name__)


@dp.message_handler(is_superuser=True, commands='update_log')
@dp.throttled(rate=30)
@dp.async_task
async def get_log(_: types.Message, config: Config):
    await send_log_files(bot, config.log.log_chat_id)


@dp.message_handler(is_superuser=True, commands='logchat')
@dp.throttled(rate=30)
async def get_logchat(message: types.Message, config: Config):
    log_ch = await bot.get_chat(config.log.log_chat_id)
    await message.answer(log_ch.invite_link, disable_notification=True)


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
@dp.throttled(rate=120)
async def generate_logchat_link(message: types.Message, config: Config):
    await message.reply(await bot.export_chat_invite_link(config.log.log_chat_id), disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
@dp.throttled(rate=30)
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')


@dp.message_handler(is_superuser=True, commands='get_out')
async def leave_chat(message: types.Message):
    await message.bot.leave_chat(message.chat.id)


@dp.message_handler(is_superuser=True, commands='dump')
@dp.throttled(rate=120)
async def get_dump(_: types.Message, config: Config):
    await send_dump_bd(config)


async def send_dump_bd(config: Config):
    with open(config.db.db_path, 'rb') as f:
        await bot.send_document(config.dump_chat_id, f)


@dp.message_handler(is_superuser=True, commands='json')
@dp.throttled(rate=120)
async def get_dump(_: types.Message, config: Config):
    dct = await UserKarma.all_to_json()

    await bot.send_document(
        config.dump_chat_id,
        ("dump.json", io.StringIO(json.dumps(dct, ensure_ascii=False, indent=2)))
    )


@dp.message_handler(is_superuser=True, commands='add_manual', commands_prefix='!')
@dp.throttled(rate=2)
async def add_manual(message: types.Message, chat: Chat, user: User):
    """
    superuser send !add_manual 46866565 666.13 то change karma of user with id 46866565 to 666.13
    :param message:
    :param chat:
    :param user:
    :return:
    """
    logger.warning("superuser {user} send command !add_manual", user=user.tg_id)
    args = message.text.partition(' ')[2]
    try:
        users_karmas = list(
            map(
                lambda x: (int(x[0]), float(x[1])),
                (uk.split(" ") for uk in args.split('\n'))
            )
        )
    except ValueError:
        return await message.reply(
            "Жду сообщение вида \n!add_manual [user_id karma]\n"
            "user_id должно быть целым числом, а карма числом с плавающей точкой"
        )
    for user_id, karma in users_karmas:
        target_user, _ = await User.get_or_create(tg_id=user_id)
        uk, _ = await UserKarma.get_or_create(user=target_user, chat=chat)
        uk.karma = karma
        await uk.save()
        logger.warning(
            "superuser {user} change manual karma for {target} to new karma {karma} in chat {chat}",
            user=user.tg_id,
            target=target_user.tg_id,
            karma=karma,
            chat=chat.chat_id
        )
    await message.reply("Кармы успешно обновлены", disable_notification=True)
