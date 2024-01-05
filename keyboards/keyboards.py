from aiogram.types import InlineKeyboardMarkup, \
                          InlineKeyboardButton, \
                          ReplyKeyboardMarkup, \
                          KeyboardButton
from loader import week
from aiogram.utils.callback_data import CallbackData


start_cb = CallbackData('start', 'course', 'group_id')
file_cb = CallbackData('file', 'file_type', 'file_id', 'update')
schedule_cb = CallbackData('schedule', 'week', 'day')


def course_kb(courses):
    keyboard = InlineKeyboardMarkup(
        row_width=2,
        resize_keyboard=True)
    for course in courses:
        keyboard.insert(
            InlineKeyboardButton(
                text=course,
                callback_data=start_cb.new(
                    course=course,
                    group_id='None'
                )
            )
        )
    return keyboard


def groups_kb(groups, course):
    keyboard = InlineKeyboardMarkup(
        row_width=2,
        resize_keyboard=True)
    groups = [group for group in groups if group['course'] == course]
    for group in groups:
        keyboard.insert(
            InlineKeyboardButton(
                text=group['name'],
                callback_data=start_cb.new(
                    course=course,
                    group_id=group['id']
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
                file_id=file_id,
                update='init'
            )
        ),
        InlineKeyboardButton(
            text='Полезный стафф',
            callback_data=file_cb.new(
                file_type='study',
                file_id=file_id,
                update='init'
            )
        ),
        InlineKeyboardButton(
            text='Не сохраняй',
            callback_data=file_cb.new(
                file_type='do_not_save',
                file_id=file_id,
                update='init'
            )
        )
    )
    return ikb


def schedule_exists_kb(file_id):
    ikb = InlineKeyboardMarkup(
        row_width=2,
        resize_keyboard=True)
    ikb.row(
        InlineKeyboardButton(
            text='Обнови',
            callback_data=file_cb.new(
                file_type='schedule',
                file_id=file_id,
                update='update'
            )
        ),
        InlineKeyboardButton(
            text='Не надо',
            callback_data=file_cb.new(
                file_type='schedule',
                file_id=file_id,
                update='dont_update'
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
