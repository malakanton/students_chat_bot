from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.callbacks import StartCallback
from keyboards.buttons import COURSES


async def course_kb(courses):
    buttons = []
    for course in courses:
        buttons.append(
            InlineKeyboardButton(
                text=COURSES[course],
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
                    course=course,
                    group_id=str(group.id)
                ).pack()
            )
        )
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()
