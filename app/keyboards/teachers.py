from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import COURSES, Confirm
from keyboards.callbacks import TeachersCallback
from typing import List
from lib.models.users import Teacher


async def teachers_list_kb(teachers: List[Teacher]):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for teacher in teachers:
        buttons.append(
            InlineKeyboardButton(
                text=teacher.name,
                callback_data=TeachersCallback(
                    id=teacher.id
                ).pack(),
            )
        )

    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()
