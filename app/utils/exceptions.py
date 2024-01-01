class KarmaError(Exception):
    def __init__(
        self, text: str = None, user_id: int = None, chat_id: int = None, *args
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


class CantChangeKarma(KarmaError):
    pass


class UserWithoutUserIdError(KarmaError):
    def __init__(self, username: str = None, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.text = (
            "Обычно так бывает, когда бот в чате недавно и ещё не видел "
            "пользователя, которому плюсанули в виде '+ @username'.",
        )


class SubZeroKarma(CantChangeKarma):
    pass


class AutoLike(CantChangeKarma):
    pass


class DontOffendRestricted(CantChangeKarma):
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


class ModerationError(KarmaError):
    def __init__(self, reason: str = None, type_event: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason = reason
        self.type_event = type_event


class CantRestrict(ModerationError):
    pass


class Throttled(RuntimeError):
    def __init__(self, key: str, chat_id: int, user_id: int, rate: int | float):
        self.key = key
        self.chat_id = chat_id
        self.user_id = user_id
        self.rate = rate


class CommandError(Exception):
    pass


class NotEnoughArguments(CommandError):
    pass


class IDParseError(CommandError):
    pass
