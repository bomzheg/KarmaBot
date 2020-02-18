class KarmaError(Exception):
    def __init__(
            self,
            text: str,
            user_id: int = None,
            chat_id: int = None,
            *args,
            **kwargs
    ):
        super(KarmaError, self).__init__(args, kwargs)
        self.text = text
        self.user_id = user_id
        self.chat_id = chat_id

    def __str__(self):
        return (
            f"Exception: {self.text}, by user {self.user_id} "
            f"in chat {self.chat_id}"
        )

    def __repr__(self):
        return str(self)
