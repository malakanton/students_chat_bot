import logging
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from loader import dp, db
from lib import lexicon as lx
from lib.misc import prep_markdown
from handlers.filters import UserFilter
from config import NOTIFICATIONS_ADVANCE
from keyboards.buttons import SwitchNotif
from keyboards.notifications import notif_kb
from keyboards.callbacks import Notifications



@dp.message(Command('notifications'), UserFilter())
async def set_notifications(message: Message):
    logging.info('notifications command')
    flag = db.check_notification_flag(message.from_user.id)[0]
    flag_wording = lx.NOTIF_FLAG[flag]
    txt = prep_markdown(
        lx.NOTIFICATION_SETTING.format(flag_wording, NOTIFICATIONS_ADVANCE)
    )
    await message.answer(
        text=txt,
        reply_markup=await notif_kb()
    )
    await message.delete()


@dp.callback_query(Notifications.filter())
async def change_week(call: CallbackQuery, callback_data: Notifications):
    flag = int(callback_data.flag == SwitchNotif.ON.name)
    await call.answer()
    user_id = call.message.chat.id
    db.set_notifications_flag(user_id, flag)
    logging.info(f'notifications flag set for user {user_id}')
    txt = prep_markdown(
        lx.NOTIFICATION_SETTING.format(lx.NOTIF_FLAG[flag], NOTIFICATIONS_ADVANCE)
    )
    await call.message.edit_text(text=txt, reply_markup=None)
