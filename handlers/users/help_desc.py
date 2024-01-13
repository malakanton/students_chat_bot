from aiogram.types import Message
from aiogram.filters import Command
from lib import lexicon as lx
from loader import dp
from handlers.filters import UserFilter, UnRegisteredUser
from lib.misc import prep_markdown


@dp.message(Command('help'), UserFilter())
async def help_cmd(message: Message):
    help_msg = prep_markdown(lx.HELP_MSG)
    await message.answer(text=help_msg, parse_mode='MarkdownV2')
    await message.delete()


@dp.message(Command('description'), UserFilter())
async def help_cmd(message: Message):
    desc_msg = prep_markdown(lx.DESCRIPTION)
    await message.answer(text=desc_msg, parse_mode='MarkdownV2')
    await message.delete()


@dp.message(Command('contacts'), UserFilter())
async def help_cmd(message: Message):
    desc_msg = prep_markdown(lx.CONTACTS)
    await message.answer(text=desc_msg, parse_mode='MarkdownV2')
    await message.delete()
