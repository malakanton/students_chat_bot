from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.callbacks import ScheduleCallback
from keyboards.buttons import ScheduleButt

import datetime as dt

# from keyboards.buttons import ScheduleButt
#
# for item in ScheduleButt:
#     print(item.name, item.value)


async def schedule_kb(week, curr_day):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for day in week.days:
        text = f'{day.code} | {str(day.date.day)}-{day.date.month}'
        if day.id == curr_day:
            text += '✅'
        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=ScheduleCallback(command=str(day.id),
                                               week=week.num).pack()
            )
        )
    control_buttons = [InlineKeyboardButton(
                text=button.value,
                callback_data=ScheduleCallback(command=button.name,
                                               week=week.num).pack())
                for button in ScheduleButt]
    kb_builder.row(*(buttons + control_buttons), width=3)
    return kb_builder.as_markup()
