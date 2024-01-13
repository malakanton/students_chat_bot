from aiogram.types import InlineKeyboardButton
from keyboards.callbacks import LibCallback
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import FileTypeButt, Confirm


async def subjects_kb(subjects: dict, file_id):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=name,
            callback_data=LibCallback(
                file_id=file_id,
                subject_id=int(subj_id),
                type='None',
                confirm='None'
            ).pack()) for name, subj_id in subjects.items()
    ]
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


async def lib_type_kb(subj_id, file_id):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=butt.value,
            callback_data=LibCallback(
                file_id=file_id,
                subject_id=subj_id,
                type=butt.name,
                confirm='None'
            ).pack()) for butt in FileTypeButt
    ]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()


async def confirm_subj_kb(file_id, subj_id, type):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=LibCallback(
                file_id=file_id,
                subject_id=subj_id,
                type=type,
                confirm=button.name).pack())
        for button in Confirm]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()