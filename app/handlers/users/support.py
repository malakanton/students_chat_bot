import re
import logging
from aiogram import F
from lib import lexicon as lx
from lib.misc import prep_markdown
from aiogram.types import Message
from handlers.filters import UserFilter, SupportFilter
from loader import dp, db, bot, users
from config import ADMIN_CHAT


@dp.message(UserFilter(), SupportFilter())
async def support_message(message: Message,
                          user_id: int,
                          text: str,
                          user_name: str,
                          date: str):
    logging.info('support tag triggered')
    user_group = db.get_user_group(user_id)
    if not user_group:
        user_group = (None, 'unregistered')
    msg = lx.FORWARD_SUPPORT.format(
        date=date,
        user_id=user_id,
        username=user_name,
        group_name=user_group[1],
        text=text
    )
    await bot.send_message(text=prep_markdown(msg), chat_id=int(ADMIN_CHAT))
    await message.reply(prep_markdown(lx.REPLY_SUPPORT))


@dp.message(F.chat.id==int(ADMIN_CHAT), F.text.startswith('#reply_support'))
async def support_reply(message: Message):
    text = message.text
    try:
        user_id_to_forward = re.findall(r'\d+', text)[0]
    except IndexError:
        await message.answer('укажи айдишник пользователя')
        return
    text = text.replace('#reply_support', '').replace(user_id_to_forward, '')
    await bot.send_message(
        chat_id=int(user_id_to_forward),
        text=prep_markdown(text)
    )
    await message.reply(f'пользователю {user_id_to_forward} отпралено сообщение:\n\n{text}')