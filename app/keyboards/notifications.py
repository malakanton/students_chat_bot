from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import NotifMenuBut, SwitchNotif
from keyboards.callbacks import NotificationMenu
from lib.dicts import NotificationsAdvance


async def notif_menu_kb(flag, push_time):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for butt in NotifMenuBut:
        if butt.name == "ADVANCE":
            flag = "None"
        buttons.append(
            InlineKeyboardButton(
                text=butt.value,
                callback_data=NotificationMenu(
                    action=butt.name,
                    flag=str(flag),
                    push_time=str(push_time).replace(":", "$"),
                ).pack(),
            )
        )
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


async def notif_kb(push_time):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for butt in NotificationsAdvance:
        button_text = SwitchNotif.ON.value.format(str(butt.value))
        buttons.append(
            InlineKeyboardButton(
                text=button_text,
                callback_data=NotificationMenu(
                    action=NotifMenuBut.ADVANCE.name,
                    flag=str(butt.name),
                    push_time=str(push_time).replace(":", "$"),
                ).pack(),
            )
        )
    buttons.append(
        InlineKeyboardButton(
            text=SwitchNotif.OFF.value,
            callback_data=NotificationMenu(
                action=NotifMenuBut.ADVANCE.name,
                flag=SwitchNotif.OFF.name,
                push_time=str(push_time).replace(":", "$"),
            ).pack(),
        )
    )
    kb_builder.row(*buttons, width=len(NotificationsAdvance))
    return kb_builder.as_markup()


async def daily_kb(flag, push_time):
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=SwitchNotif.SET.value,
            callback_data=NotificationMenu(
                action=SwitchNotif.SET.name,
                flag=str(flag),
                push_time=str(push_time).replace(":", "$"),
            ).pack(),
        ),
        InlineKeyboardButton(
            text=SwitchNotif.OFF.value,
            callback_data=NotificationMenu(
                action=SwitchNotif.OFF.name,
                flag=str(flag),
                push_time=str(push_time).replace(":", "$"),
            ).pack(),
        ),
    ]
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()
