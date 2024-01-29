from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbacks import Notifications
from keyboards.buttons import SwitchNotif


async def notif_kb():
    buttons = []
    for butt in SwitchNotif:
        buttons.append(
            InlineKeyboardButton(
                text=butt.value,
                callback_data=Notifications(
                    flag=butt.name
                ).pack())
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
