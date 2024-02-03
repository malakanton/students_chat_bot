from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.callbacks import Notifications
from keyboards.buttons import SwitchNotif
from lib.dicts import NotificationsAdvance


async def notif_kb():
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for butt in NotificationsAdvance:
        button_text = SwitchNotif.ON.value.format(str(butt.value))
        buttons.append(
            InlineKeyboardButton(
                text=button_text,
                callback_data=Notifications(
                    flag=str(butt.name)
                ).pack())
        )
    buttons.append(
        InlineKeyboardButton(
            text=SwitchNotif.OFF.value,
            callback_data=Notifications(
                    flag=SwitchNotif.OFF.name
                ).pack()
        )
    )
    kb_builder.row(*buttons, width=len(NotificationsAdvance))
    return kb_builder.as_markup()
