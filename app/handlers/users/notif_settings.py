import logging
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from loader import dp, db
from lib import lexicon as lx
from lib.misc import prep_markdown, logging_msg
from lib.dicts import NotificationsAdvance
from handlers.filters import UserFilter
from keyboards.buttons import SwitchNotif
from keyboards.notifications import notif_kb
from keyboards.callbacks import Notifications


@dp.message(Command('notifications'), UserFilter())
async def set_notifications(message: Message):
    logging.info(logging_msg(message, 'notifications command'))
    try:
        flag = db.check_notification_flag(message.from_user.id)[0]
        txt = get_notifications_text(flag)
        await message.answer(
            text=txt,
            reply_markup=await notif_kb()
        )
    except IndexError:
        logging.warning('No user notifications info in database')
    await message.delete()


@dp.callback_query(Notifications.filter())
async def change_notifications_flag(call: CallbackQuery, callback_data: Notifications):
    # flag = int(callback_data.flag == SwitchNotif.ON.name)
    flag = callback_data.flag
    if flag == SwitchNotif.OFF.name:
        flag = 0
    else:
        flag = NotificationsAdvance[flag].value
    await call.answer()
    user_id = call.message.chat.id
    db.set_notifications_flag(user_id, flag)
    logging.info(logging_msg(call, 'notifications flag set for user'))
    txt = get_notifications_text(flag, end_of_dialog=True)
    await call.message.edit_text(text=txt, reply_markup=None)


def get_notifications_text(
        flag: int,
        end_of_dialog: bool = False
) -> str:
    status = int(flag != 0)
    flag_wording = lx.NOTIF_FLAG[status]
    txt = lx.NOTIFICATIONS_STATUS.format(flag_wording)
    if status and not end_of_dialog:
        txt += lx.NOTIFICATIONS_ON.format(flag) + lx.NOTIFICATIONS_ON_BEGIN
    elif status:
        txt += lx.NOTIFICATIONS_ON.format(flag) + lx.NOTIFICATIONS_ON_OFF_END
    elif end_of_dialog:
        txt += lx.NOTIFICATIONS_ON_OFF_END
    else:
        txt += lx.NOTIFICATIONS_OFF
    return prep_markdown(txt)
