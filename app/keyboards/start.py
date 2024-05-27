from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import COURSES, Confirm
from keyboards.callbacks import StartCallback


async def course_kb(courses):
    buttons = []
    for course in courses:
        buttons.append(
            InlineKeyboardButton(
                text=COURSES[course],
                callback_data=StartCallback(
                    course=course, group_id="None", confirm="None"
                ).pack(),
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def groups_kb(groups, course):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    groups = [group for group in groups if group.course == course]
    groups = sorted(groups, key=lambda x: x.name)
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=group.name,
                callback_data=StartCallback(
                    course=course, group_id=str(group.id), confirm="None"
                ).pack(),
            )
        )
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


async def confirm_kb(course, group):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=StartCallback(
                course=course, group_id=str(group.id), confirm=button.name
            ).pack(),
        )
        for button in Confirm
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()
