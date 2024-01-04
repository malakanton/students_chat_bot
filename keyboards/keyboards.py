from aiogram.types import InlineKeyboardMarkup, \
                          InlineKeyboardButton, \
                          ReplyKeyboardMarkup, \
                          KeyboardButton
from loader import week, db
from aiogram.utils.callback_data import CallbackData
# from keyboards_buttons import *


start_cb = CallbackData('start', 'group_id')
file_cb = CallbackData('file', 'file_type', 'file_id')
schedule_cb = CallbackData('schedule', 'week', 'day')
sch_exists_cb = CallbackData('schedule_exists', 'update')


def start_kb(groups):
    keyboard = InlineKeyboardMarkup(
        row_width=2,
        resize_keyboard=True)
    for group_id, group_name in groups.items():
        keyboard.insert(
            InlineKeyboardButton(
                text=group_name,
                callback_data=start_cb.new(
                    group_id=group_id
                )
            )
        )
    return keyboard


def kb(commands: list):
    keyboard = ReplyKeyboardMarkup(
        row_width=4,
        resize_keyboard=True,
        one_time_keyboard=True)
    for command in commands:
        keyboard.insert(
            KeyboardButton(command)
               )
    return keyboard


def file_kb(file_id):
    ikb = InlineKeyboardMarkup(
        row_width=3,
        resize_keyboard=True)
    ikb.row(
        InlineKeyboardButton(
            text='Расписание',
            callback_data=file_cb.new(
                file_type='schedule',
                file_id=file_id
            )
        ),
        InlineKeyboardButton(
            text='Учебные материалы',
            callback_data=file_cb.new(
                file_type='study_file',
                file_id=file_id
            )
        ),
    )
    return ikb


def schedule_exists_kb():
    ikb = InlineKeyboardMarkup(
        row_width=2,
        resize_keyboard=True)
    ikb.row(
        InlineKeyboardButton(
            text='Обнови',
            callback_data=sch_exists_cb.new(
                update='yes'
            )
        ),
        InlineKeyboardButton(
            text='Не надо',
            callback_data=sch_exists_cb.new(
                update='no'
            )
        ),
    )
    return ikb


def schedule_kb(today):
    ikb = InlineKeyboardMarkup(
        row_width=3)
    ikb.row(InlineKeyboardButton(
        text='Сегодня',
        callback_data=schedule_cb.new(
            week=today.week,
            day=today.day_of_week
        )
    ),
        InlineKeyboardButton(
            text='Вся неделя',
            callback_data=schedule_cb.new(
                week=today.week,
                day=0
            )
        )
    )
    ikb.add()
    for i, day in week.days.items():
        print(i, day)
        button = InlineKeyboardButton(
                text=day.name,
                callback_data=schedule_cb.new(
                    week=today.week,
                    day=day.id
                )
        )
        if i == 0:
            ikb.add(button)
        else:
            ikb.insert(button)
    return ikb
