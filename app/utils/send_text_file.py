import textwrap
from asyncio import sleep

from aiogram.utils.markdown import hbold, hpre
from loguru import logger

from app.utils.log import log_path

MAX_MESSAGE_SYMBOLS = 4000

PAUSE_SEC = 3


async def split_text_file(file_name):
    buffer_lines = f"{hbold(file_name)}:\n"
    rez = list()
    with open(file_name, 'r+') as in_file:

        for line in in_file:

            if len(line) > MAX_MESSAGE_SYMBOLS:
                rez.append(buffer_lines)
                buffer_lines = ""
                separated_text = [hpre(line) for line in textwrap.wrap(line, MAX_MESSAGE_SYMBOLS)]
                rez.extend(separated_text)
            elif len(buffer_lines) + len(line) > MAX_MESSAGE_SYMBOLS:
                rez.append(buffer_lines)
                buffer_lines = ""
            else:
                line = hpre(line)
                buffer_lines += line
        if len(buffer_lines) > 0:
            rez.append(buffer_lines)
        in_file.truncate(0)
    return rez


async def send_list_messages(bot, list_msg, chat_id):
    for msg in list_msg:
        await bot.send_message(
            chat_id,
            msg,
            disable_notification=True,
            parse_mode="HTML"
        )
        await sleep(PAUSE_SEC)


async def send_text_file(bot, file_name, chat_id):
    parts_log = await split_text_file(file_name)
    if len(parts_log) == 1 and len(parts_log[0].splitlines()) == 1:
        return
    await send_list_messages(bot, parts_log, chat_id)


async def send_log_files(bot, chat_id):
    logger.debug('send logs file')
    for file_name in log_path.glob('*.log'):
        await send_text_file(bot, file_name, chat_id)
