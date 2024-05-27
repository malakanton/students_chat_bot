import re
from typing import Optional, Union

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from handlers.routers import users_router
from handlers.states import PushNotoficationsState
from keyboards.buttons import NotifMenuBut, SwitchNotif
from keyboards.callbacks import NotificationMenu
from keyboards.notifications import daily_kb, notif_kb, notif_menu_kb
from lib import lexicon as lx
from lib.dicts import NotificationsAdvance
from lib.logs import logging_msg
from lib.misc import prep_markdown
from loader import db, scheduler
from loguru import logger


@users_router.message(Command("notifications"))
async def set_notifications(message: Message):
    logger.info(logging_msg(message, "notifications command"))
    user_id = message.from_user.id
    try:
        flag = db.check_notification_flag(user_id)[0]
        push_time = db.get_users_push_time(user_id)
        txt = get_notifications_text(flag, str(push_time))
        await message.answer(
            text=txt, reply_markup=await notif_menu_kb(flag, push_time)
        )
    except IndexError:
        logger.warning("No user notifications info in database")
    await message.delete()


# выбрал настройки ежедневных уведомлений
@users_router.callback_query(
    NotificationMenu.filter(F.action == NotifMenuBut.DAILY.name)
)
async def change_pushing_time(call: CallbackQuery, callback_data: NotificationMenu):
    logger.info(logging_msg(call))
    await call.answer()
    flag = callback_data.flag
    push_time = callback_data.push_time.replace("$", ":")

    txt = prep_markdown(lx.PUSHING_OFF)
    if push_time:
        txt = prep_markdown(lx.PUSHING_ON.format(push_time))

    await call.message.edit_text(text=txt, reply_markup=await daily_kb(flag, push_time))


# если выбрал устаноивить время
@users_router.callback_query(NotificationMenu.filter(F.action == SwitchNotif.SET.name))
async def set_push_time(
    call: CallbackQuery, callback_data: NotificationMenu, state: FSMContext
):
    logger.info(logging_msg(call))
    await call.answer()
    await call.message.delete()

    await call.message.answer(prep_markdown(lx.PUSH_TIME_MESSAGE))
    await state.set_state(PushNotoficationsState.set_time)


# если пользователь выбрал выключить
@users_router.callback_query(NotificationMenu.filter(F.action == SwitchNotif.OFF.name))
async def turn_off_push_notif(call: CallbackQuery, callback_data: NotificationMenu):
    logger.info(logging_msg(call))
    await call.answer()

    user_id = call.message.chat.id
    flag = db.set_push_time(user_id)
    job_id = str(user_id)
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

    await finish_dialog(flag, None, call.message)


# ввод времени с клавиатуры
@users_router.message(StateFilter(PushNotoficationsState.set_time))
async def receive_time_from_user(message: Message, state: FSMContext):
    push_time = check_correct_time(message.text)

    if push_time:
        from lib.notifications import add_daily_push_for_user

        await state.clear()
        logger.info(logging_msg(message, "Valid time format"))

        user_id = message.from_user.id
        flag = db.set_push_time(user_id, push_time)
        add_daily_push_for_user(user_id, push_time, scheduler)
        await finish_dialog(flag, push_time, message)

    else:
        logger.warning(logging_msg(message, "Invalid time format"))
        await message.answer(prep_markdown(lx.INVALID_PUSH_TIME))


# выбрал уведомления перед уроком
@users_router.callback_query(
    NotificationMenu.filter(
        (F.action == NotifMenuBut.ADVANCE.name) & (F.flag == "None")
    )
)
async def change_notifications_flag(
    call: CallbackQuery, callback_data: NotificationMenu
):
    logger.info(logging_msg(call))
    await call.answer()

    push_time = callback_data.push_time.replace("$", ":")

    txt = prep_markdown(lx.NOTIFICATIONS_SET_TEXT)

    await call.message.edit_text(
        text=txt,
        reply_markup=await notif_kb(push_time),
    )


# выбрано время уведомлений перед уроком
@users_router.callback_query(
    NotificationMenu.filter(F.action == NotifMenuBut.ADVANCE.name)
)
async def final_settings(call: CallbackQuery, callback_data: NotificationMenu):
    logger.info(logging_msg(call))
    await call.answer()

    user_id = call.message.chat.id
    flag = callback_data.flag
    if flag == SwitchNotif.OFF.name:
        flag = 0

    else:
        flag = NotificationsAdvance[flag].value
    db.set_notifications_flag(user_id, flag)
    push_time = callback_data.push_time.replace("$", ":")

    await finish_dialog(flag, push_time, call.message)


# финал любого сценария
async def finish_dialog(
    flag: Union[int, str], push_time: str, message: Message
) -> None:

    params = {
        "text": get_notifications_text(flag, push_time, end_of_dialog=True),
        "reply_markup": None,
    }
    try:
        await message.edit_text(**params)

    except TelegramBadRequest:
        await message.answer(**params)


def get_notifications_text(
    flag: Union[int, str], push_time: Optional[str], end_of_dialog: bool = False
) -> str:
    txt = ""
    status = int(flag != 0)
    txt += lx.NOTIF_FLAG[status]
    if status:
        txt = txt.format(flag)

    push_status = int(1 if push_time else 0)
    push_wording = lx.NOTIF_PUSH[push_status]
    if push_status:
        if len(push_time) > 5:
            push_time = push_time[:-3]
        push_wording = push_wording.format(push_time)
    txt += "\n" + push_wording
    if end_of_dialog:
        txt = lx.NOTIFICATIONS_CHANGE + txt + lx.NOTIFICATIONS_DIALOG_END
    else:
        txt += lx.NOTIFICATIONS_ON_BEGIN

    return prep_markdown(txt)


def check_correct_time(users_input: str) -> str:
    match = re.match(r"^([01]?[0-9]|2[0-3])[\s\-?.:^ю]+([0-5][0-9])$", users_input)

    if match:
        corrected_time = re.sub(r"[\s\-?.^ю]+", ":", users_input)
        return corrected_time

    return ""
