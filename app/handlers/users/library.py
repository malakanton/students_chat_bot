from loader import dp, users
from aiogram.types import Message
from lib import lexicon as lx
from handlers.filters import UserFilter
from aiogram.filters import Command
from lib.misc import prep_markdown, logging_msg
import logging


@dp.message(Command('library'),
            UserFilter())
async def library(message: Message):
    logging.info(logging_msg(message, 'library command in private chat'))
    uid = message.from_user.id
    if uid in users.unreg:
        msg = prep_markdown(lx.USER_GROUP_NOT_REGISTER)
    else:
        msg = prep_markdown(lx.NO_LIBRARY_YET)
    await message.answer(msg)
