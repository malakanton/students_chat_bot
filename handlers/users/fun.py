from loader import dp, db, bot
from aiogram.types import Message
from aiogram import F
from handlers.filters import UserFilter
import logging
from lib.misc import test_users_dates
import re
import datetime as dt


@dp.message(UserFilter(),
            F.content_type == 'text',
            ~F.contains('/'))
async def set_date(message: Message):
    text = message.text
    user_id = message.from_user.id
    await message.answer('test')
