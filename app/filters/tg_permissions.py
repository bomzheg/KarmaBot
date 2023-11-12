# from https://github.com/aiogram/bot/blob/master/app/filters/has_permissions.py
import logging
from dataclasses import dataclass
from typing import Any

from aiogram import Bot, types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import BaseFilter

from app.infrastructure.database.models import Chat
from app.services.find_target_user import get_target_user

logger = logging.getLogger(__name__)


@dataclass
class HasPermissions(BaseFilter):
    """
    Validate the user has specified permissions in chat
    """

    can_post_messages: bool = False
    can_edit_messages: bool = False
    can_delete_messages: bool = False
    can_restrict_members: bool = False
    can_promote_members: bool = False
    can_change_info: bool = False
    can_invite_users: bool = False
    can_pin_messages: bool = False

    ARGUMENTS = {
        "user_can_post_messages": "can_post_messages",
        "user_can_edit_messages": "can_edit_messages",
        "user_can_delete_messages": "can_delete_messages",
        "user_can_restrict_members": "can_restrict_members",
        "user_can_promote_members": "can_promote_members",
        "user_can_change_info": "can_change_info",
        "user_can_invite_users": "can_invite_users",
        "user_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "user_member"

    def __post_init__(self):
        self.required_permissions = {
            arg: True for arg in self.ARGUMENTS.values() if getattr(self, arg)
        }

    def _get_cached_value(self, user: types.User, chat: Chat) -> types.ChatMember | None:
        return None  # TODO

    def _set_cached_value(self, user: types.User, chat: Chat, _member: types.ChatMember):
        return None  # TODO

    async def _get_chat_member(
        self, update: types.TelegramObject, user: types.User, chat: Chat, bot: Bot
    ):
        chat_member = self._get_cached_value(user, chat)

        if chat_member is None:
            admins = await bot.get_chat_administrators(chat.chat_id)
            target_user_id = self.get_target_id(update, user, bot)
            if target_user_id is None:
                return False
            try:
                chat_member = next(filter(lambda member: member.user.id == target_user_id, admins))
            except StopIteration:
                return False
            self._set_cached_value(user, chat, chat_member)
        return chat_member

    async def __call__(
        self,
        update: types.TelegramObject,
        event_from_user: types.User,
        chat: Chat,
        bot: Bot,
    ) -> bool | dict[str, Any]:
        chat_member = await self._get_chat_member(update, event_from_user, chat, bot)
        if not chat_member:
            return False
        if chat_member.status == ChatMemberStatus.CREATOR:
            return chat_member
        for permission, _value in self.required_permissions.items():
            if not getattr(chat_member, permission):
                return False

        return {self.PAYLOAD_ARGUMENT_NAME: chat_member}

    def get_target_id(self, update: types.TelegramObject, user: types.User, bot: Bot) -> int | None:
        return user.id


@dataclass
class TargetHasPermissions(HasPermissions):
    """
    Validate the target user has specified permissions in chat
    """

    can_be_same: bool = False
    can_be_bot: bool = False

    def get_target_id(self, message: types.Message, user: types.User, bot: Bot) -> int | None:
        target_user = get_target_user(message, self.can_be_same, self.can_be_bot)
        if target_user is None:
            return None
        return target_user.id


class BotHasPermissions(HasPermissions):
    """
    Validate the bot has permissions in chat
    """

    ARGUMENTS = {
        "bot_can_post_messages": "can_post_messages",
        "bot_can_edit_messages": "can_edit_messages",
        "bot_can_delete_messages": "can_delete_messages",
        "bot_can_restrict_members": "can_restrict_members",
        "bot_can_promote_members": "can_promote_members",
        "bot_can_change_info": "can_change_info",
        "bot_can_invite_users": "can_invite_users",
        "bot_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "bot_member"

    def get_target_id(self, message: types.Message, user: types.User, bot: Bot) -> int | None:
        return bot.id
