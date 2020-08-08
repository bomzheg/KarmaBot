from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

from app.config import PLUS_TRIGGERS, MINUS, PLUS_EMOJI, MINUS_EMOJI
from app.misc import dp
from app.models.chat import Chat


@dp.throttled(rate=3)
@dp.message_handler(commands=["start"], commands_prefix='!/')
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        "Я бот для подсчёта кармы в группе, просто добавьте меня "
        "в группу и плюсуйте друг другу в карму"
    )


@dp.throttled(rate=3)
@dp.message_handler(commands=["help"], commands_prefix='!')
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply(
        (
            'Плюсануть в карму можно начав сообщение с "{plus}". '
            'Минусануть:  "{minus}".\n'
            'Чтобы выбрать пользователя - нужно ответить реплаем на сообщение пользователя '
            'или упомянуть его через @ (работает даже если у пользователя нет username).\n'
            '!top - топ юзеров по карме\n'
            '!about - информция о боте\n'
            '!me - посмотреть свою карму\n'
        ).format(plus='", "'.join([*PLUS_TRIGGERS, *PLUS_EMOJI]), minus='", "'.join([*MINUS, *MINUS_EMOJI]))
    )


@dp.throttled(rate=3)
@dp.message_handler(commands=["about"], commands_prefix='!')
async def cmd_about(message: types.Message):
    logger.info("User {user} about", user=message.from_user.id)
    await message.reply('Исходники по ссылке https://github.com/bomzheg/KarmaBot')


@dp.throttled(rate=3)
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
