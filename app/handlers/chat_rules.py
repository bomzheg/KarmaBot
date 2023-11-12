from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.handlers import keyboards as kb


async def lmgify_cmd(m: Message, command: CommandObject, bot: Bot):
    if command.args:
        args = command.args
    else:
        args = "Как правильно задавать вопросы в сообществе"
    await bot.send_message(
        chat_id=m.chat.id,
        text="⁉ Вы можете получить ответ на свой вопрос перейдя по ссылке ниже:",
        reply_markup=kb.get_lmgfy_kb(args),
        reply_to_message_id=m.reply_to_message.message_id,
    )
    await m.delete()


async def paste_cmd(m: Message, bot: Bot):
    await bot.send_message(
        chat_id=m.chat.id,
        text="📝 Для того чтобы поделиться кодом или текстом ошибки воспользуйтесь сервисами:",
        reply_markup=kb.get_paste_kb(),
        reply_to_message_id=m.reply_to_message.message_id,
    )
    await m.delete()


async def nometa_cmd(m: Message, bot: Bot):
    await bot.send_message(
        chat_id=m.chat.id,
        text="🎙 Пожалуйста, не задавайте мета-вопросы в чате!",
        reply_markup=kb.get_nometa_kb(),
        reply_to_message_id=m.reply_to_message.message_id,
    )
    await m.delete()


async def xy_problem_cmd(m: Message, bot: Bot):
    await bot.send_message(
        chat_id=m.chat.id,
        text="🎙 Похоже мы столкнулись с XY problem!",
        reply_markup=kb.get_xy_problem_kb(),
        reply_to_message_id=m.reply_to_message.message_id,
    )
    await m.delete()


async def delete_me_cmd(m: Message):
    await m.delete()


def setup() -> Router:
    router = Router(name=__name__)
    router.message.register(lmgify_cmd, Command("go", prefix="!"), F.reply_to_message)
    router.message.register(paste_cmd, Command("paste", prefix="!"), F.reply_to_message)
    router.message.register(nometa_cmd, Command("nm", prefix="!"), F.reply_to_message)
    router.message.register(xy_problem_cmd, Command("xy", prefix="!"), F.reply_to_message)
    router.message.register(delete_me_cmd, Command("go", "paste", "nm", prefix="!"))
    return router
