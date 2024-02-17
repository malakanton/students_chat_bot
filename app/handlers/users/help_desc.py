import logging
from loader import dp
from lib import lexicon as lx
from aiogram.types import Message
from handlers.routers import users_router
from lib.misc import prep_markdown
from lib.logs import logging_msg
from aiogram.filters import Command
from handlers.filters import UserFilter


@users_router.message(Command('help'))
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'help command in private chat'))
    help_msg = prep_markdown(lx.HELP_MSG)
    await message.answer(text=help_msg)
    await message.delete()


@users_router.message(Command('description'))
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'description command in pricate chat'))
    desc_msg = prep_markdown(lx.DESCRIPTION)
    await message.answer(text=desc_msg)
    await message.delete()


@users_router.message(Command('contacts'))
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'contacts command in pricate chat'))
    desc_msg = prep_markdown(lx.CONTACTS)
    await message.answer(text=desc_msg)
    await message.delete()
