import logging
from app.lib import lexicon as lx
from aiogram.types import Message
from app.handlers.filters import UserFilter, SupportFilter
from app.loader import dp, db, bot
from app.config import ADMIN_CHAT


@dp.message(UserFilter(), SupportFilter())
async def support_message(message: Message,
                          user_id: int,
                          text: str,
                          user_name: str,
                          date: str):
    logging.info('support tag triggered')
    user_group = db.get_user_group(user_id)
    if not user_group:
        user_group = 'unregistered'
    msg = lx.FORWARD_SUPPORT.format(
        date=date,
        user_id=user_id,
        username=user_name,
        group_name=user_group[1],
        text=text
    )
    await bot.send_message(text=msg, chat_id=int(ADMIN_CHAT))
    await message.reply(lx.REPLY_SUPPORT)
