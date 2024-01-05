from aiogram.utils.text_decorations import html_decoration as hd
from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base
from .enums import ChatType


class Chat(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    type_: Mapped[ChatType] = mapped_column(Enum(ChatType))
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # user_karma = relation
    # settings = relation

    @property
    def mention(self):
        return hd.link(self.title, f"t.me/{self.username}")

    def __str__(self):
        rez = f"<Chat type={self.type_} " \
              f"id={self.chat_id} " \
              f"title={self.title} " \
              f"username={self.username} " \
              f"description={self.description}>"
        if self.username:
            rez += f"username=@{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez
