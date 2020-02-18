import textwrap
from asyncio import sleep

from loguru import logger

from app.misc import bot
from app.misc import dp
from app.utils.logging import log_path


async def split_text_file(file_name):
    in_file = open(file_name, 'r+')
    buffer_lines = f"{file_name}:\n"
    rez = list()
    for line in in_file:
        line = line.replace("&", "&amp;")
        line = line.replace("<", "&lt;")
        line = line.replace(">", "&amp;")
        if len(buffer_lines) + len(line) > 2980:
            rez.append(buffer_lines)
            buffer_lines = ""
        buffer_lines += line
    if 0 < len(buffer_lines) < 2980:
        rez.append(buffer_lines)
    elif len(buffer_lines) >= 2980:
        splitted_text = textwrap.wrap(buffer_lines, 2980)
        for text in splitted_text:
            rez.append(text)
    in_file.truncate(0)
    in_file.close()
    return rez


PRE_O = '<pre>'
PRE_C = '</pre>'


async def send_list_messages(list_msg, chat_id):
    for msg in list_msg:
        await bot.send_message(chat_id, f"{PRE_O}{msg}{PRE_C}", disable_notification=True, parse_mode="HTML")
        await sleep(1)


async def send_text_file(file_name, chat_id):
    parts_log = await split_text_file(file_name)
    await send_list_messages(parts_log, chat_id)


@dp.async_task
async def send_log_files(chat_id):
    logger.debug('send logs file')
    for file_name in log_path.glob('*.log'):
        await send_text_file(file_name, chat_id)
