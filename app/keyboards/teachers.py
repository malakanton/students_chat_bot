from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import TeachersButt
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
                text=teacher.name,
                callback_data=TeachersCallback(
                    id=teacher.id,
                    paginate=None,
                    index=0
                ).pack(),
            )
        )

    for button in TeachersButt:
        buttons.append(InlineKeyboardButton(
            text=button.value,
            callback_data=TeachersCallback(
                    id=-1,
                    paginate=button.name,
                    index=from_idx
                ).pack(),
        ))


    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()
