from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import CancelButt, Confirm, FileTypeButt
from keyboards.callbacks import LibCallback
from lib.models.files import File


async def subjects_kb(subjects: dict, file_id: int = -1):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=name,
            callback_data=LibCallback(
                file_id=file_id, subject_id=int(subj_id), type="None", confirm="None"
            ).pack(),
        )
        for name, subj_id in subjects.items()
    ]
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


async def lib_type_kb(
    subj_id: int, file_id: int = -1, chosen_types: list = list(), back: bool = False
):
    kb_builder = InlineKeyboardBuilder()
    if not chosen_types:
        chosen_types = FileTypeButt.__members__
    buttons = [
        InlineKeyboardButton(
            text=butt.value,
            callback_data=LibCallback(
                file_id=file_id, subject_id=subj_id, type=butt.name, confirm="None"
            ).pack(),
        )
        for butt in FileTypeButt
        if butt.name in chosen_types
    ]
    if back:
        buttons.append(
            InlineKeyboardButton(
                text=CancelButt.BACK.value,
                callback_data=LibCallback(
                    file_id=file_id,
                    subject_id=subj_id,
                    type="None",
                    confirm=CancelButt.BACK.name,
                ).pack(),
            )
        )
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()


async def choose_file_kb(files: list[File]):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=file.file_name,
            callback_data=LibCallback(
                file_id=-1,
                subject_id=file.subj_id,
                type=file.file_type,
                confirm=str(idx),
            ).pack(),
        )
        for idx, file in enumerate(files)
    ]
    buttons.append(
        InlineKeyboardButton(
            text=CancelButt.BACK.value,
            callback_data=LibCallback(
                file_id=-1, subject_id=0, type="None", confirm=CancelButt.BACK.name
            ).pack(),
        )
    )
    kb_builder.row(*(buttons), width=1)
    return kb_builder.as_markup()


async def confirm_subj_kb(file_id, subj_id, type):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=LibCallback(
                file_id=file_id, subject_id=subj_id, type=type, confirm=button.name
            ).pack(),
        )
        for button in Confirm
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()
