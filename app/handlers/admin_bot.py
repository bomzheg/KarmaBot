import io
import json

from aiogram import types
from loguru import logger

from app import config
from app.misc import bot, dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.utils.send_text_file import send_log_files


@dp.throttled(rate=30)
@dp.message_handler(is_superuser=True, commands='update_log')
async def get_log(_: types.Message):
    await send_log_files(config.LOG_CHAT_ID)


@dp.throttled(rate=30)
@dp.message_handler(is_superuser=True, commands='logchat')
async def get_logchat(_: types.Message):
    log_ch = (await bot.get_chat(config.LOG_CHAT_ID)).invite_link
    await bot.send_message(config.GLOBAL_ADMIN_ID, log_ch, disable_notification=True)


@dp.throttled(rate=120)
@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
async def generate_logchat_link(message: types.Message):
    await message.reply(await bot.export_chat_invite_link(config.LOG_CHAT_ID), disable_notification=True)


@dp.throttled(rate=30)
@dp.message_handler(is_superuser=True, commands='idchat')
async def get_idchat(message: types.Message):
    await message.reply(message.chat.id, disable_notification=True)


@dp.throttled(rate=30)
@dp.message_handler(is_superuser=True, commands=["exception"])
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')


@dp.throttled(rate=120)
@dp.message_handler(is_superuser=True, commands='dump')
async def get_dump(_: types.Message):
    await send_dump_bd()


async def send_dump_bd():
    with open(config.DB_PATH, 'rb') as f:
        await bot.send_document(config.DUMP_CHAT_ID, f)


@dp.throttled(rate=120)
@dp.message_handler(is_superuser=True, commands='json')
async def get_dump(_: types.Message):
    dct = await UserKarma.all_to_json()

    await bot.send_document(
        config.DUMP_CHAT_ID,
        ("dump.json", io.StringIO(json.dumps(dct, ensure_ascii=False, indent=2)))
    )


@dp.throttled(rate=2)
@dp.message_handler(is_superuser=True, commands='add_manual', commands_prefix='!')
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
