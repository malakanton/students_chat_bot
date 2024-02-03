import sys
import datetime as dt
from .models import Today
from aiogram import types
from config import HOST, HOST_LOCAL, PORT, PORT_LOCAL
from aiogram.types import Message, CallbackQuery


test_users_dates = {}


def get_today(set_date: dt.datetime=None):
    today = dt.datetime.now()
    if set_date:
        today = set_date
    current_week = today.isocalendar()[1]
    day_of_week = today.weekday() + 1
    today = Today(
        date=today.date(),
        week=current_week,
        day_of_week=day_of_week
    )
    return today


def chat_msg_ids(
        call: types.CallbackQuery
) -> tuple:
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    return chat_id, message_id


def valid_schedule_format(
        filename: str
) -> bool:
    import re
    return re.match(r'^[Оо]чно[-_]заочное.отделение.{1,3}[0-9].*\.pdf$', filename)


def prep_markdown(
        text: str
) -> str:
    MARKDOWN = '.()-!#='
    for ch in MARKDOWN:
        text = text.replace(ch, '\\' + ch)
    text = text.replace('<LINK>\\', '')
    return text


def get_host_port():
    if sys.platform == 'darwin':
        return HOST_LOCAL, PORT_LOCAL
    return HOST, PORT


def logging_msg(
        update: Message | CallbackQuery,
        logging_text: str = '',
) -> str:
    user_id = update.from_user.id
    chat_type, chat_id, command = '', '', ''
    if isinstance(update, Message):
        command = update.text
        chat_type = update.chat.type
        chat_id = update.chat.id
    elif isinstance(update, CallbackQuery):
        command = update.data
        chat_type = update.message.chat.type
        chat_id = update.message.chat.id
    return f'user_id: {user_id} chat_id: {chat_id} chat_type: {chat_type} command: {command} message: {logging_text}'
