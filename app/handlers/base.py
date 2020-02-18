from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp, CommandStart
from loguru import logger

from app.misc import dp
from app.models.user import User


@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message, user: User):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    logger.debug(user)
    await message.answer('messages.START_MSG')


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply('messages.HELP_MSG')


@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    await message.reply('messages.ABOUT_MSG')


@dp.message_handler(state='*', commands='cancel')
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info(f'Cancelling state {current_state}')
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('messages.MSG_CANCEL', reply_markup=types.ReplyKeyboardRemove())
