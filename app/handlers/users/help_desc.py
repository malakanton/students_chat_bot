from loader import dp
from lib import lexicon as lx
from aiogram.types import Message
from lib.misc import prep_markdown
from aiogram.filters import Command
from handlers.filters import UserFilter


@dp.message(Command('help'), UserFilter())
async def help_cmd(message: Message):
    help_msg = prep_markdown(lx.HELP_MSG)
    await message.answer(text=help_msg)
    await message.delete()


@dp.message(Command('description'), UserFilter())
async def help_cmd(message: Message):
    desc_msg = prep_markdown(lx.DESCRIPTION)
    await message.answer(text=desc_msg)
    await message.delete()


@dp.message(Command('contacts'), UserFilter())
async def help_cmd(message: Message):
    desc_msg = prep_markdown(lx.CONTACTS)
    await message.answer(text=desc_msg)
    await message.delete()
