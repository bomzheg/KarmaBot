from aiogram import types
from loguru import logger

from app import config
from app.misc import bot, dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.utils.log import StreamToLogger
from app.utils.send_text_file import send_log_files

_logger = StreamToLogger(logger)


@dp.message_handler(chat_id=config.GLOBAL_ADMIN_ID, commands='cancel_jobs')
async def cancel_jobs(message: types.Message):
    from app.services.apscheduller import scheduler
    logger.warning("removing all jobs")
    scheduler.print_jobs(out=_logger)
    scheduler.remove_all_jobs()
    await message.reply("Данные удалены")


@dp.message_handler(is_superuser=True, commands='update_log')
async def get_log(_: types.Message):
    await send_log_files(config.LOG_CHAT_ID)


@dp.message_handler(is_superuser=True, commands='logchat')
async def get_logchat(_: types.Message):
    log_ch = (await bot.get_chat(config.LOG_CHAT_ID)).invite_link
    await bot.send_message(config.GLOBAL_ADMIN_ID, log_ch, disable_notification=True)


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
async def generate_logchat_link(message: types.Message):
    await message.reply(await bot.export_chat_invite_link(config.LOG_CHAT_ID), disable_notification=True)


@dp.message_handler(is_superuser=True, commands='idchat')
async def get_idchat(message: types.Message):
    await message.reply(message.chat.id, disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')


@dp.message_handler(is_superuser=True, commands='dump')
async def get_dump(_: types.Message):
    await bot.send_document(
        config.DUMP_CHAT_ID,
        open(
            config.DB_PATH,
            'rb'
        )
    )


@dp.message_handler(is_superuser=True, commands='add_manual', commands_prefix='!')
async def add_manual(message: types.Message, chat: Chat):
    args = message.text.partition(' ')[2]
    logger.debug(float(args.split(' ')[1]))
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
        user, _ = await User.get_or_create(tg_id=user_id)
        uk, _ = await UserKarma.get_or_create(user=user, chat=chat)
        uk.karma = karma
        await uk.save()
    await message.reply("Кармы успешно обновлены", disable_notification=True)
