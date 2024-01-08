from aiogram.types import Message
from aiogram.filters import Command
from lib import lexicon as lx
from loader import dp


@dp.message(Command('help'))
async def help_cmd(message: Message):
    await message.answer(text=lx.HELP_MSG, parse_mode='MarkdownV2')
    await message.delete()
