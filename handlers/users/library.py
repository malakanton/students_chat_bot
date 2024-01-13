from loader import dp, users
from aiogram.types import Message
import lib.lexicon as lx
from handlers.filters import UserFilter
from aiogram.filters import Command
import logging
from lib.misc import prep_markdown


@dp.message(Command('library'),
            UserFilter())
async def library(message: Message):
    uid = message.from_user.id
    if uid in users.unreg:
        msg = prep_markdown(lx.USER_GROUP_NOT_REGISTER)
    else:
        msg = prep_markdown(lx.NO_LIBRARY_YET)
    await message.answer(msg, parse_mode='MarkdownV2')