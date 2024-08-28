from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import COURSES, Confirm, Start, StudyFormKb
from keyboards.callbacks import StartCallback
from lib.models.group import Groups, StudyForm
from typing import List


async def role_selector_kb():
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=button.name,
        )
        for button in Start
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()


async def choose_study_form():
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=button.name,
        )
        for button in StudyFormKb
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()


async def course_kb(courses: List[int], form: StudyForm):
    buttons = []
    for course in courses:
        buttons.append(
            InlineKeyboardButton(
                text=COURSES[course],
                callback_data=StartCallback(
                    course=course, form=form.value, group_id=None, confirm=None, group_name=None
                ).pack(),
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def groups_kb(groups: Groups, course: int, form: int):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    groups = [group for group in groups.groups if group.course == course]
    groups = sorted(groups, key=lambda x: x.name)
    for group in groups:
        buttons.append(
            InlineKeyboardButton(
                text=group.name,
                callback_data=StartCallback(
                    course=course, form=form, group_id=group.id, confirm=None, group_name=group.name
                ).pack(),
            )
        )
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


async def confirm_kb(group_id: int, group_name: str):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=StartCallback(
                course=None, form=None, group_id=group_id, confirm=button.name, group_name=group_name
            ).pack()
        )
        for button in Confirm
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()
