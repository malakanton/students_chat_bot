import datetime as dt
import os

from aiogram import F
from aiogram.types import Message
from lib.config.config import cfg
from handlers.routers import groups_router


@groups_router.message(
    ~F.text.startswith("/"), ~F.text.startswith("#"), F.content_type == "text"
)
async def write_messages(message: Message):
    chat_id = message.chat.id
    filepath = cfg.CHATS_HISTORY.format(chat_id)
    msg_text = await form_msg_text(message)
    if not os.path.exists(filepath):
        await new_chat_write(filepath, msg_text)
    else:
        await process_text_file(filepath, msg_text)


async def new_chat_write(filepath: str, msg_text: str) -> None:
    with open(filepath, "w") as file:
        file.write(msg_text)


async def process_text_file(filepath: str, add_msg: str) -> None:
    with open(filepath, "r") as file:
        text = file.read()
    messages_list = text.split("<MSG>")[1:]
    if len(messages_list) >= cfg.MESSAGES_TO_KEEP:
        messages_list.pop(0)
    messages_list = ["<MSG>" + msg for msg in messages_list]
    messages_list.append(add_msg)
    text_updated = "".join(messages_list)
    with open(filepath, "w") as file:
        file.write(text_updated)


async def form_msg_text(message: Message) -> str:
    user_name = message.from_user.first_name
    if message.from_user.last_name:
        user_name += " " + message.from_user.last_name
    date = message.date + dt.timedelta(hours=3)
    date = date.strftime("%Y-%m-%d %H:%M")
    msg_text = f"<MSG>[{date}] {user_name}\n"
    msg_text += f"{message.text}\n\n"
    return msg_text
