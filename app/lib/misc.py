import datetime as dt
import yaml

from aiogram import types

from .models.lessons import Today

test_users_dates = {}


def get_today(set_date: dt.datetime = None):
    today = dt.datetime.now()
    if set_date:
        today = set_date
    current_week = today.isocalendar()[1]
    day_of_week = today.weekday() + 1
    today = Today(date=today.date(), week=current_week, day_of_week=day_of_week)
    return today


def chat_msg_ids(call: types.CallbackQuery) -> tuple:
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    return chat_id, message_id


def valid_schedule_format(filename: str) -> bool:
    import re

    return re.match(r"^[Оо]чно[-_]заочное.отделение.{1,3}[0-9].*\.pdf$", filename)


def prep_markdown(text: str) -> str:
    MARKDOWN = ".()-!#=+|"
    for ch in MARKDOWN:
        text = text.replace(ch, "\\" + ch)
    text = text.replace("<LINK>\\", "")
    return text


class Lexicon:

    def __init__(self, lexicon_file_path: str):
        with open(lexicon_file_path, "r") as file:
            docs = yaml.safe_load(file)

        for name, value in docs.items():
            setattr(self, name, value)
