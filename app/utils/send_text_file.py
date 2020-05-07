import textwrap
import html
from asyncio import sleep

from loguru import logger

from app.misc import bot
from app.misc import dp
from app.utils.log import log_path

MAX_MESSAGE_SYMBOLS = 4000

PAUSE_SEC = 3


def escape_line(line):
    rez = line.replace("&", "&amp;")
    rez = rez.replace("<", "&lt;")
    rez = rez.replace(">", "&gt;")
    return rez


async def split_text_file(file_name):
    buffer_lines = f"{file_name}:\n"
    rez = list()
    with open(file_name, 'r+') as in_file:

        for line in in_file:
            line = html.escape(line)

            if len(line) > MAX_MESSAGE_SYMBOLS:
                rez.append(buffer_lines)
                buffer_lines = ""
                splitted_text = textwrap.wrap(line, MAX_MESSAGE_SYMBOLS)
                rez.extend(splitted_text)
            elif len(buffer_lines) + len(line) > MAX_MESSAGE_SYMBOLS:
                rez.append(buffer_lines)
                buffer_lines = ""
            else:
                buffer_lines += line
        if len(buffer_lines) > 0:
            rez.append(buffer_lines)
        in_file.truncate(0)
    return rez


def pre_format(msg):
    pre_o = '<pre>'
    pre_c = '</pre>'
    return f"{pre_o}{msg}{pre_c}"


async def send_list_messages(list_msg, chat_id):
    for msg in list_msg:
        await bot.send_message(
            chat_id,
            pre_format(msg),
            disable_notification=True,
            parse_mode="HTML"
        )
        await sleep(PAUSE_SEC)


async def send_text_file(file_name, chat_id):
    parts_log = await split_text_file(file_name)
    if len(parts_log) == 1 and len(parts_log[0].splitlines()) == 1:
        return
    await send_list_messages(parts_log, chat_id)


@dp.async_task
async def send_log_files(chat_id):
    logger.debug('send logs file')
    for file_name in log_path.glob('*.log'):
        await send_text_file(file_name, chat_id)
