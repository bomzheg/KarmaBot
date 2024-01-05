import enum


class ChatType(str, enum.Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = 'channel'
