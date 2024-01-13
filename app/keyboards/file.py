from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.callbacks import FileCallback
from app.keyboards.buttons import FileButt, SchdUpdButt


async def file_kb(file_id, schedule=True):
    buttons = [
        InlineKeyboardButton(
            text=FileButt.CANCEL.value,
            callback_data=FileCallback(
                file_type=FileButt.CANCEL.name,
                file_id=file_id,
                update='init'
            ).pack()
        ),
        InlineKeyboardButton(
            text=FileButt.STUDY.value,
            callback_data=FileCallback(
                file_type=FileButt.STUDY.name,
                file_id=file_id,
                update='init'
            ).pack()
        )
    ]
    if schedule:
        buttons.append(
            InlineKeyboardButton(
                text=FileButt.SCHEDULE.value,
                callback_data=FileCallback(
                    file_type=FileButt.SCHEDULE.name,
                    file_id=file_id,
                    update='init'
                ).pack()
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def schedule_exists_kb(file_id):
    buttons = [
        InlineKeyboardButton(
            text=SchdUpdButt.UPDATE.value,
            callback_data=FileCallback(
                file_type=FileButt.SCHEDULE.name,
                file_id=file_id,
                update=SchdUpdButt.UPDATE.value
            ).pack()
        ),
        InlineKeyboardButton(
            text=SchdUpdButt.KEEP.value,
            callback_data=FileCallback(
                file_type=FileButt.SCHEDULE.name,
                file_id=file_id,
                update=SchdUpdButt.KEEP.value
            ).pack()
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])



