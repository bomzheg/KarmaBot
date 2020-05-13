from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp, CommandStart
from loguru import logger

from app.config import PLUS, MINUS
from app.misc import dp
from app.models.chat import Chat


@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        "Бот для изменения кармы в группе, просто добавьте "
        "в группу и плюсуйте друг другу в карму"
    )


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply(
        (
            'Плюсануть в карму можно начав сообщение с "{plus}". '
            'Минусануть:  "{minus}".\n'
            'Чтобы выбрать пользователя - нужно ответить реплаем на сообщение пользователя '
            'или упомянуть его через @ (работает даже если у пользователя нет username.'
        ).format(plus='", "'.join(PLUS), minus='", "'.join(MINUS))
    )


@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    await message.reply('Исходники по ссылке https://github.com/bomzheg/KarmaBot')


@dp.message_handler(state='*', commands='cancel')
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info(f'Cancelling state {current_state}')
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Диалог прекращён, данные удалены', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=types.ContentTypes.MIGRATE_TO_CHAT_ID)
async def chat_migrate(message: types.Message, chat: Chat):
    old_id = message.chat.id
    new_id = message.migrate_to_chat_id
    chat.chat_id = new_id
    await chat.save()
    logger.info(f"Migrate chat from {old_id} to {new_id}")
