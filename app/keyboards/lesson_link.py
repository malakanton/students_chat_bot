from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbacks import LessonLinkCallback
from keyboards.buttons import FileButt
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import datetime as dt


async def link_kb(lessons: list, msg_id:int):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=get_button_name(subj_name, date, time),
            callback_data=LessonLinkCallback(
                msg_id=msg_id,
                date=str(date),
                time=str(time).replace(':', '$'),
                subj_id=subj_id
            ).pack()) for date, time, subj_id, subj_name in lessons
    ]
    buttons.append(InlineKeyboardButton(
        text=FileButt.CANCEL.value,
        callback_data=LessonLinkCallback(
            msg_id=msg_id,
            date='',
            time='',
            subj_id=0
        ).pack()
    ))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def get_button_name(subj_name:str, date:dt.date, time:dt.time):
    text = ''
    text += date.strftime("%d-%m") + ' '
    text += time.strftime("%H:%M") + ' '
    text += subj_name
    return text
