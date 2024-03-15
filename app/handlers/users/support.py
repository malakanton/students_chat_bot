import re
from loguru import logger
from aiogram import F
from lib import lexicon as lx
from lib.misc import prep_markdown
from lib.logs import logging_msg
from aiogram.types import Message, CallbackQuery
from keyboards.callbacks import ConfirmCallback
from handlers.routers import users_router, groups_router
from handlers.filters import SupportFilter
from loader import db, bot
from config import ADMIN_CHAT
from keyboards.universal import send_newsletter_kb
from keyboards.buttons import NewsLetter


@users_router.message(SupportFilter())
async def support_message(message: Message,
                          user_id: int,
                          text: str,
                          first_name: str,
                          user_name: str,
                          date: str):
    logger.info(logging_msg(message, 'support hashtag processing'))
    user_group = db.get_user_group(user_id)
    if not user_group:
        user_group = (None, 'unregistered')
    if not user_name:
        user_name = ''
    msg = lx.FORWARD_SUPPORT.format(
        date=date,
        user_id=user_id,
        first_name=first_name,
        username=user_name,
        group_name=user_group[1],
        text=text
    )
    await bot.send_message(text=prep_markdown(msg), chat_id=int(ADMIN_CHAT))
    await message.reply(prep_markdown(lx.REPLY_SUPPORT))


@groups_router.message(
    F.chat.id == int(ADMIN_CHAT),
    F.text.startswith('#reply_support')
)
async def support_reply(message: Message):
    text = message.text
    try:
        user_id_to_forward = re.findall(r'\d+', text)[0]
    except IndexError:
        await message.answer('укажи айдишник пользователя')
        return
    text = text.replace('#reply_support', '').replace(user_id_to_forward, '').strip()
    text = prep_markdown(text)
    await bot.send_message(
        chat_id=int(user_id_to_forward),
        text=text
    )
    await message.reply(f'пользователю {user_id_to_forward} отпралено сообщение:\n{text}')


@groups_router.message(
    F.chat.id == int(ADMIN_CHAT),
    F.text.startswith('#newsletter')
)
async def send_newsletter(message: Message):
    text = message.text.replace('#newsletter', '').strip()
    text = prep_markdown(text)
    await message.answer(
        text=text,
        reply_markup=await send_newsletter_kb()
    )
    await message.delete()


@groups_router.callback_query(ConfirmCallback.filter(F.cnf.in_(NewsLetter._member_names_)))
async def confirm_subj(call: CallbackQuery, callback_data: ConfirmCallback):
    response = callback_data.cnf
    if response == NewsLetter.OK.name:
        msgs_sent = await send_to_users(call.message.text)
        reply = f'Отправил {msgs_sent} пользователям!'
    else:
        reply = 'Ок, не буду отправлять'
    await call.answer(reply, show_alert=True)
    await call.message.edit_reply_markup(reply_markup=None)


async def send_to_users(text: str) -> int:
    user_ids = db.get_users_ids('all')
    for user_id in user_ids:
        await bot.send_message(
            chat_id=user_id,
            text=text
        )
    return len(user_ids)
