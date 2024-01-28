import logging
from loader import dp, db
from lib import lexicon as lx
from aiogram.types import Message, CallbackQuery
from config import NOTIFICATIONS_ADVANCE
from lib.misc import prep_markdown
from aiogram.filters import Command
from handlers.filters import UserFilter
from keyboards.notifications import notif_kb
from keyboards.callbacks import Notifications


@dp.message(Command('notifications'), UserFilter)
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


@dp.callback_query(Notifications.filter())
async def change_week(call: CallbackQuery, callback_data: Notifications):
    if callback_data.flag == 'ON':
        flag = 1
    else:
        flag = 0
    await call.answer()
    user_id = call.message.chat.id
    db.set_notifications_flag(user_id, flag)
    logging.info(f'notifications flag set for user {user_id}')
    txt = prep_markdown(
        lx.NOTIFICATION_SETTING.format(lx.NOTIF_FLAG[flag], NOTIFICATIONS_ADVANCE)
    )
    await call.message.edit_text(text=txt, reply_markup=None)
