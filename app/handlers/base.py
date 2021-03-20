from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hpre, hbold
from loguru import logger

from app.misc import dp
from app.models.db import Chat


@dp.message_handler(commands=["start"], commands_prefix='!/')
@dp.throttled(rate=3)
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        "Я бот для подсчёта кармы в группе, просто добавьте меня "
        "в группу и плюсуйте друг другу в карму.\n"
        "<code>!help</code> - справка о командах\n"
        "<code>!about</code> - информация о боте и его исходники "
    )


@dp.message_handler(commands=["help"], commands_prefix='!/')
@dp.throttled(rate=3)
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply(
        '➕Плюсануть в карму можно начав сообщение со спасибо или плюса.\n'
        '➖Минусануть - с минуса.\n'
        '📩Чтобы выбрать пользователя - нужно ответить реплаем на сообщение пользователя '
        'или упомянуть его через @ (работает даже если у пользователя нет username).\n'
        '🦾Сила, с которой пользователь меняет другим карму, зависит от собственной кармы, '
        'чем она больше, тем больше будет изменение кармы у цели '
        '(вычисляется как корень из кармы)\n'
        '🤖Основные команды:\n'
        '<code>!top</code> [chat_id] - топ юзеров по карме для текущего чата или для чата с chat_id \n'
        '<code>!about</code> - информация о боте и его исходники\n'
        '<code>!me</code> - посмотреть свою карму (желательно это делать в личных сообщениях с ботом)\n'
        '<code>!report</code> {{реплаем}} - пожаловаться на сообщение модераторам\n'
        '<code>!idchat</code> - показать Ваш id, id чата и, '
        'если имеется, - id пользователя, которому Вы ответили командой'
    )


@dp.message_handler(commands=["about"], commands_prefix='!')
@dp.throttled(rate=3)
async def cmd_about(message: types.Message):
    logger.info("User {user} about", user=message.from_user.id)
    await message.reply('Исходники по ссылке https://github.com/bomzheg/KarmaBot')


@dp.message_handler(commands='idchat', commands_prefix='!')
@dp.throttled(rate=30)
async def get_idchat(message: types.Message):
    text = (
        f"id этого чата: {hpre(message.chat.id)}\n"
        f"Ваш id: {hpre(message.from_user.id)}"
    )
    if message.reply_to_message:
        text += (
            f"\nid {hbold(message.reply_to_message.from_user.full_name)}: "
            f"{hpre(message.reply_to_message.from_user.id)}"
        )
    await message.reply(text, disable_notification=True)


@dp.message_handler(state='*', commands='cancel')
@dp.throttled(rate=3)
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
