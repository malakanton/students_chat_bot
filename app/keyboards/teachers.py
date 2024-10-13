from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import TeachersButt, Confirm
from keyboards.callbacks import TeachersCallback
from typing import List
from lib.models.users import Teacher

TEACHERS_PER_PAGE = 20


async def teachers_list_kb(teachers: List[Teacher], from_idx: int):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    to_idx = from_idx+TEACHERS_PER_PAGE
    for teacher in teachers[from_idx:to_idx]:
        buttons.append(
            InlineKeyboardButton(
                text=teacher.last_name + ' ' + teacher.initials,
                callback_data=TeachersCallback(
                    id=teacher.id,
                    paginate=None,
                    index=0,
                    confirm=None,
                ).pack(),
            )
        )
    kb_builder.row(*buttons, width=2)

    if len(buttons) % 2 == 0:
        kb_builder.adjust(2)

    kb_builder_paginate = InlineKeyboardBuilder()
    paginate_buttons = []
    for button in TeachersButt:
        paginate_buttons.append(InlineKeyboardButton(
            text=button.value,
            callback_data=TeachersCallback(
                    id=-1,
                    paginate=button.name,
                    index=from_idx,
                    confirm=None,
                ).pack(),
        ))

    kb_builder_paginate.row(*paginate_buttons)

    kb_builder.attach(kb_builder_paginate)
    return kb_builder.as_markup()


async def teacher_confirm_kb(teacher_id: int):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=TeachersCallback(
                id=teacher_id, index=0, paginate=None, confirm=button.name
            ).pack()
        )
        for button in Confirm
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()
