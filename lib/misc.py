import datetime as dt
from models import Today
from aiogram import types


def get_today():
    today = dt.datetime.now()
    current_week = today.isocalendar()[1]
    day_of_week = today.weekday() + 1
    today = Today(
        date=str(today.date()),
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


def validate_schedule_format(
        filename: str
) -> bool:
    if (
        filename.endswith('.pdf') and
        'очно_заочное_' in filename.lower()
    ):
        return True


