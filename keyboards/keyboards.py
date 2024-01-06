from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loader import week
from keyboards.callbacks import FileCallback, StartCallback, ScheduleCallback


async def course_kb(courses):
    buttons = []
    for course in courses:
        buttons.append(
            InlineKeyboardButton(
                text=str(course),
                callback_data=StartCallback(
                    course=course,
                    group_id='None'
                ).pack())
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def groups_kb(groups, course):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    groups = [group for group in groups if group.course == course]
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=group.name,
                callback_data=StartCallback(
                    course=str(course),
                    group_id=group.id
                ).pack()
            )
        )
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


# def create_inline_kb(width: int,
#                      *args: str,
#                      **kwargs: str) -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     buttons = []
#     if args:
#         for button in args:
#             buttons.append(InlineKeyboardButton(
#                 text=LEXICON[button] if button in LEXICON else button,
#                 callback_data=button))
#     if kwargs:
#         for button, text in kwargs.items():
#             buttons.append(InlineKeyboardButton(
#                 text=text,
#                 callback_data=button))
#     kb_builder.row(*buttons, width=width)
#     return kb_builder.as_markup()


async def file_kb(file_id):
    buttons = [
        InlineKeyboardButton(
            text='Расписание',
            callback_data=FileCallback(
                file_type='schedule',
                file_id=file_id,
                update='init'
            ).pack()
        ),
        InlineKeyboardButton(
            text='Полезный стафф',
            callback_data=FileCallback(
                file_type='study',
                file_id=file_id,
                update='init'
            ).pack()
        ),
        InlineKeyboardButton(
            text='Не сохраняй',
            callback_data=FileCallback(
                file_type='do_not_save',
                file_id=file_id,
                update='init'
            ).pack()
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def schedule_exists_kb(file_id):
    buttons = [
        InlineKeyboardButton(
            text='Обнови',
            callback_data=FileCallback(
                file_type='schedule',
                file_id=file_id,
                update='update'
            ).pack()
        ),
        InlineKeyboardButton(
            text='Не надо',
            callback_data=FileCallback(
                file_type='schedule',
                file_id=file_id,
                update='dont_update'
            ).pack()
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def schedule_kb(today):
    ikb = InlineKeyboardMarkup(
        row_width=3)
    ikb.row(InlineKeyboardButton(
        text='Сегодня',
        callback_data=ScheduleCallback(
            week=today.week,
            day=today.day_of_week
        ).pack()
    ),
        InlineKeyboardButton(
            text='Вся неделя',
            callback_data=ScheduleCallback(
                week=today.week,
                day=0
            ).pack()
        )
    )
    ikb.add()
    for i, day in week.days.items():
        print(i, day)
        button = InlineKeyboardButton(
                text=day.name,
                callback_data=ScheduleCallback(
                    week=today.week,
                    day=day.id
                ).pack()
        )
        if i == 0:
            ikb.add(button)
        else:
            ikb.insert(button)
    return ikb
