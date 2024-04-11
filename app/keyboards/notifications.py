from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.callbacks import Notifications, NotificationMenu
from lib import lexicon as lx
from lib.misc import prep_markdown
# from keyboards.buttons import SwitchNotif
from lib.dicts import NotificationsAdvance

from app.keyboards.buttons import NotifMenuBut, SwitchNotif


async def notif_menu_kb(flag, push_time):
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for butt in NotifMenuBut:
        buttons.append(
            InlineKeyboardButton(
                text=butt.value,
                callback_data=NotificationMenu(
                    action=str(butt.name),
                    flag=str(flag),
                    push_time=str(push_time).replace(':', '$')
                ).pack())
        )
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


async def notif_kb(flag, push_time):
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
                    push_time=str(push_time).replace(':', '$')
                ).pack())
        )
    buttons.append(
        InlineKeyboardButton(
            text=SwitchNotif.OFF.value,
            callback_data=NotificationMenu(
                    action=NotifMenuBut.ADVANCE.name,
                    flag=SwitchNotif.OFF.name,
                    push_time=str(push_time).replace(':', '$')
                ).pack()
        )
    )
    kb_builder.row(*buttons, width=len(NotificationsAdvance))
    return kb_builder.as_markup()


async def daily_kb(flag, push_time):
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(
        text=prep_markdown(lx.PUT_TIME),
        callback_data=NotificationMenu(
            action=NotifMenuBut.DAILY.name,
            flag=str(flag),
            push_time=str(push_time).replace(':', '$')
        ).pack()
    ), InlineKeyboardButton(
        text=SwitchNotif.OFF.value,
        callback_data=NotificationMenu(
            action=NotifMenuBut.DAILY.name,
            flag=SwitchNotif.OFF.name,
            push_time=str(push_time).replace(':', '$')
        ).pack()
    )]
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()
