import importlib

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions
from aiogram.utils.markdown import hbold, hpre

from app.infrastructure.database.models import Chat
from app.infrastructure.database.repo.chat import ChatRepo
from app.utils.log import Logger

logger = Logger(__name__)
router = Router(name=__name__)


@router.message(Command("start", prefix="!/"))
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        "Я бот для подсчёта кармы в группе, просто добавьте меня "
        "в группу и плюсуйте друг другу в карму.\n"
        "<code>!help</code> – справка о командах\n"
        "<code>!about</code> – информация о боте и его исходники"
    )


@router.message(Command("help", prefix="!/"))
async def cmd_help(message: types.Message):
    logger.info(
        "User {user} read help in {chat}",
        user=message.from_user.id,
        chat=message.chat.id,
    )
    await message.reply(
        "➕Плюсануть в карму можно начав сообщение со спасибо или плюса.\n"
        "➖Минусануть – с минуса.\n"
        "🦾Сила, с которой пользователь меняет другим карму, зависит от собственной кармы, чем она "
        "больше, тем больше будет изменение.\n\n"
        "🤖Основные команды:\n"
        "<code>!top</code> [chat_id] – топ юзеров по карме в чате\n"
        "<code>!me</code> – посмотреть собственную карму\n"
        "<code>!report</code> &lt;реплаем&gt; – пожаловаться на сообщение модераторам\n"
        "/settings – настройки чата\n\n"
        "🗂Другие разделы:\n"
        "/moderator_help – справка по командам модераторов\n"
        "/advanced_help – продвинутая справка по командам бота"
    )


@router.message(Command("moderator_help", prefix="!/"))
async def cmd_moderator_help(message: types.Message):
    logger.info(
        "User {user} read moderator help in {chat}",
        user=message.from_user.id,
        chat=message.chat.id,
    )
    await message.reply(
        "📩Для выбора пользователя нужно ответить реплаем на сообщение пользователя или упомянуть "
        "его через @. "
        "Все команды из данного списка требуют указания пользователя одним из способов.\n\n"
        "💢Команды модераторов:\n"
        "<code>!ro</code> [время] – ограничить пользователю возможность "
        "писать в чате\n"
        "<code>!ban</code> [время] – заблокировать пользователя\n"
        "<code>!warn</code> – выдать предупреждение пользователю\n"
        "<code>!info</code> – показать информацию о пользователе"
        # no info here about import karma. it's not so public API
    )


@router.message(Command("advanced_help", prefix="!/"))
async def cmd_advanced_help(message: types.Message):
    logger.info(
        "User {user} read advanced help in {chat}",
        user=message.from_user.id,
        chat=message.chat.id,
    )
    await message.reply(
        "➕Плюсануть в карму можно начав сообщение со спасибо или плюса.\n"
        "➖Минусануть – с минуса.\n"
        "📩Для выбора пользователя нужно ответить реплаем на сообщение пользователя или упомянуть "
        "его через @. "
        "Необязательные параметры указываются в квадратных скобках, а обязательные – в угловых.\n"
        "🦾Сила, с которой пользователь меняет другим карму, зависит от собственной кармы, чем она "
        "больше, тем больше будет изменение. "
        "Максимально возможное изменение кармы вычисляется как корень из собственной кармы.\n\n"
        "🤖Основные команды:\n"
        "<code>!top</code> [chat_id] – топ юзеров по карме в текущем или указанном чате. "
        "Смотреть топ другого чата можно только в личных сообщениях с ботом\n"
        "<code>!me</code> – посмотреть собственную карму\n"
        "<code>!report</code> &lt;реплаем&gt; – пожаловаться на сообщение модераторам\n"
        "/settings – настройки чата\n\n"
        "💢Команды модераторов:\n"
        "<code>!ro</code> [время] – ограничить пользователю возможность "
        "писать в чате. Пользователь сможет использовать только реакции\n"
        "<code>!ban</code> [время] – заблокировать пользователя\n"
        "<code>!warn</code> – выдать предупреждение пользователю\n"
        "<code>!info</code> – показать информацию о пользователе: изменения кармы, "
        "ограничения и предупреждения\n\n"
        "🔮Вспомогательные команды:\n"
        "<code>!idchat</code> [пользователь] – показать собственный ID, чата и пользователя, "
        "если указан\n"
        "<code>!go</code> [запрос] – поиск в Google по запросу, если указан\n"
        "<code>!paste</code> – сервисы для обмена кодом\n"
        "<code>!nm</code> – информация о мета-вопросах\n"
        "<code>!xy</code> – информация о XY problem\n"
    )


@router.message(Command("privacy"))
async def privacy(message: types.Message):
    with (
        importlib.resources.path("app.infrastructure.assets", "privacy.txt") as path,
        path.open("r") as f,
    ):
        await message.reply(f.read())


@router.message(Command("about", prefix="!"))
async def cmd_about(message: types.Message):
    logger.info("User {user} about", user=message.from_user.id)
    repo_url = "https://github.com/bomzheg/KarmaBot"
    await message.reply(
        text=f"Исходники по ссылке: {repo_url}",
        link_preview_options=LinkPreviewOptions(url=repo_url, prefer_small_media=True),
    )


@router.message(Command("idchat", prefix="!"))
async def get_idchat(message: types.Message):
    text = f"id этого чата: {hpre(message.chat.id)}\nВаш id: {hpre(message.from_user.id)}"
    if message.reply_to_message:
        text += (
            f"\nid {hbold(message.reply_to_message.from_user.full_name)}: "
            f"{hpre(message.reply_to_message.from_user.id)}"
        )
    await message.reply(text, disable_notification=True)


@router.message(Command("cancel"))
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info(f"Cancelling state {current_state}")
    # Cancel state and inform user about it
    await state.clear()
    # And remove keyboard (just in case)
    await message.reply(
        "Диалог прекращён, данные удалены", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(F.message.content_types == types.ContentType.MIGRATE_TO_CHAT_ID)
async def chat_migrate(message: types.Message, chat: Chat, chat_repo: ChatRepo):
    old_id = message.chat.id
    new_id = message.migrate_to_chat_id
    chat.chat_id = new_id
    await chat_repo.save(chat)
    logger.info(f"Migrate chat from {old_id} to {new_id}")
