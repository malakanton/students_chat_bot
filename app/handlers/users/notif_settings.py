import asyncio
import re
from datetime import datetime
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from loguru import logger
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from loader import dp, db
from lib import lexicon as lx
from lib.misc import prep_markdown
from lib.logs import logging_msg
from lib.dicts import NotificationsAdvance
from handlers.routers import users_router
from keyboards.buttons import SwitchNotif
from keyboards.notifications import notif_kb, notif_menu_kb, daily_kb
from keyboards.callbacks import Notifications
from aiogram import F

from app.handlers.states import PushNotoficationsState
from app.keyboards.buttons import NotifMenuBut
from app.keyboards.callbacks import NotificationMenu


@users_router.message(Command('notifications'))
async def set_notifications(message: Message):
    logger.info(logging_msg(message, 'notifications command'))
    try:
        flag = db.check_notification_flag(message.from_user.id)[0]
        push_time = db.get_users_push_time().get(message.from_user.id)
        txt = get_notifications_text(flag, push_time)
        await message.answer(
            text=txt,
            reply_markup=await notif_menu_kb(flag, push_time)
        )
    except IndexError:
        logger.warning('No user notifications info in database')
    await message.delete()


@users_router.callback_query(NotificationMenu.filter(F.action == NotifMenuBut.DAILY.name))
async def change_pushing_time(call: CallbackQuery, callback_data: NotificationMenu, state: FSMContext):
    print("change_pushing_time вызван")
    action = callback_data.action
    flag = callback_data.flag
    push_time = callback_data.push_time.replace('$', ':')
    txt = prep_markdown(lx.PUSHING_OFF)
    sent_message = await call.message.answer(
                text=txt,
                reply_markup=await daily_kb(flag, push_time)
            )
    await call.message.delete()
    if flag == SwitchNotif.OFF.name:
        push_time = None
        await call.answer()
        user_id = call.message.chat.id
        db.set_push_time(user_id, push_time)
        callback_data.action = NotifMenuBut.FINISH.name
        await final_settings(call, callback_data)
        await sent_message.delete()
    else:
        await call.message.answer('введи время')
        await state.set_state(PushNotoficationsState.set_time)


@users_router.message(StateFilter(PushNotoficationsState.set_time))
async def check_correct_time(message: Message, state: FSMContext):
    print("check_correct_time вызван")
    users_input = message.text
    if re.match(r'^([01][0-9]|2[0-3]):([0-5][0-9])$', users_input):
        await state.clear()
        hours, minutes = map(int, users_input.split(':'))
        time = datetime.strptime(users_input, '%H:%M').time()
        user_id = message.from_user.id
        db.set_push_time(user_id, time)
        await message.answer(f'ты установил время {message.text}')
        flag = db.check_notification_flag(message.from_user.id)[0]
        push_time = users_input
        txt = get_notifications_text(flag, push_time, end_of_dialog=True)
        await message.answer(
            text=txt,
            reply_markup=None)
    else:
        await message.answer('неверный формат времени')


@users_router.callback_query(NotificationMenu.filter(F.action == NotifMenuBut.ADVANCE.name))
async def change_notifications_flag(call: CallbackQuery, callback_data: NotificationMenu):
    action = callback_data.action
    flag = callback_data.flag
    push_time = callback_data.push_time.replace('$', ':')
    txt = prep_markdown(lx.NOTIFICATIONS_OFF)
    await call.message.answer(
        text=txt,
        reply_markup=await notif_kb(flag, push_time),
    )
    # await call.message.delete()
    if flag == SwitchNotif.OFF.name:
        flag = 0

    else:
        flag = NotificationsAdvance[flag].value
    await call.answer()
    user_id = call.message.chat.id
    db.set_notifications_flag(user_id, flag)
    logger.info(logging_msg(call, 'notifications flag set for user'))
    # await sent_message.delete()
    callback_data.action = NotifMenuBut.FINISH.name
    await final_settings(call, callback_data)
    await call.message.edit_text(text=txt, reply_markup=None)


@users_router.callback_query(NotificationMenu.filter(F.action == NotifMenuBut.FINISH.name))
async def final_settings(call: CallbackQuery, callback_data: NotificationMenu):
    action = callback_data.action
    user_id = call.message.chat.id
    flag = db.check_notification_flag(user_id)[0]
    push_time = db.get_users_push_time().get(user_id)
    txt = get_notifications_text(flag, push_time, end_of_dialog=True)
    await call.message.answer(
        text=txt,
        reply_markup=None)


def get_notifications_text(
        flag: int,
        push_time: str,
        end_of_dialog: bool = False
) -> str:
    status = int(flag != 0)
    flag_wording = lx.NOTIF_FLAG[status]
    txt = lx.NOTIFICATIONS_STATUS.format(flag_wording)
    if status and not end_of_dialog:
        txt += lx.NOTIFICATIONS_ON.format(flag)
    elif status:
        txt += lx.NOTIFICATIONS_ON.format(flag) + lx.NOTIFICATIONS_ON_OFF_END
    elif end_of_dialog:
        txt += lx.NOTIFICATIONS_ON_OFF_END
    else:
        txt += lx.NOTIFICATIONS_OFF
    push_status = int(push_time is not None)
    push_wording = lx.NOTIF_PUSH[push_status]
    txt_push = lx.NOTIFICATIONS_STATUS.format(push_wording)
    if push_status and not end_of_dialog:
        txt_push += lx.PUSHING_ON.format(push_time) + lx.NOTIFICATIONS_ON_BEGIN
    elif push_status:
        txt_push += lx.PUSHING_ON.format(push_time) + lx.NOTIFICATIONS_ON_OFF_END
    elif end_of_dialog:
        txt_push += lx.NOTIFICATIONS_ON_OFF_END
    else:
        txt_push += lx.PUSHING_OFF
    txt += "\n" + txt_push
    return prep_markdown(txt)




