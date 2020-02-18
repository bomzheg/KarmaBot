def get_text(message):
    if message.text:
        return message.text
    elif message.caption:
        return message.caption
    else:
        return ""


async def serialize_message(message):
    rez = f"message ID {message.message_id}. "
    if message.chat.type == "channel":
        rez += (
            f"В канале(!), с ID {message.chat.id}, названием {message.chat.title}, "
            f"юзернеймом @{str(message.chat.username)} было отправлено сообщение {str(message.text)}"
        )
        return rez

    if message.chat.type == "private":
        rez += "В личке с ботом, "
    elif message.chat.type == "group":
        rez += f"В группе с ID {message.chat.id}, "
    elif message.chat.type == "supergroup":
        rez += f"В супергруппе с ID {message.chat.id}, "

    rez += (
        f"пользователь с ID {message.from_user.id},по имени "
        f"{message.from_user.first_name} {message.from_user.last_name}"
    )

    if message.from_user.username:
        rez += f" с юзернеймом @{message.from_user.username}"

    if get_text(message):
        rez += f" написал: {get_text(message)}"
    else:
        rez += "отправил нетекстовое сообщение"
    return rez
