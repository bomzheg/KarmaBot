class KarmaError(Exception):
    def __init__(
            self,
            text: str = None,
            user_id: int = None,
            chat_id: int = None,
            *args
    ):
        super(KarmaError, self).__init__(text, args)
        self.text = text
        self.user_id = user_id
        self.chat_id = chat_id

    def __str__(self):
        text = f"{self.__class__.__name__}: {self.text}"
        if self.user_id is not None:
            text += f", by user {self.user_id} "
        if self.chat_id is not None:
            text += f"in chat {self.chat_id}"
        return text

    def __repr__(self):
        return str(self)


class UserWithoutUserIdError(KarmaError):
    def __init__(self, username: str = None, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.text = (
            "Обычно так бывает, когда бот в чате недавно и ещё не видел "
            "пользователя, которому плюсанули в виде '+ @username'.",
        )


class SubZeroKarma(KarmaError):
    pass


class AutoLike(KarmaError):
    pass


class CantImportFromAxenia(KarmaError):
    pass


class TimedeltaParseError(KarmaError):
    pass


class ToLongDuration(TimedeltaParseError):
    pass


class InvalidFormatDuration(TimedeltaParseError):
    pass


class NotHaveNeighbours(KarmaError):
    pass
