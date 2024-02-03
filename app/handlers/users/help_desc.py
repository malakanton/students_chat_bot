import logging
from loader import dp
from lib import lexicon as lx
from aiogram.types import Message
from lib.misc import prep_markdown, logging_msg
from aiogram.filters import Command
from handlers.filters import UserFilter


@dp.message(Command('help'), UserFilter())
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'help command in private chat'))
    help_msg = prep_markdown(lx.HELP_MSG)
    await message.answer(text=help_msg)
    await message.delete()


@dp.message(Command('description'), UserFilter())
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'description command in pricate chat'))
    desc_msg = prep_markdown(lx.DESCRIPTION)
    await message.answer(text=desc_msg)
    await message.delete()


@dp.message(Command('contacts'), UserFilter())
async def help_cmd(message: Message):
    logging.info(logging_msg(message, 'contacts command in pricate chat'))
    desc_msg = prep_markdown(lx.CONTACTS)
    await message.answer(text=desc_msg)
    await message.delete()
