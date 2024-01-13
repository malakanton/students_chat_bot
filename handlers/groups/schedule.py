from aiogram.types import Message
from aiogram.filters import Command
from lib import lexicon as lx
from loader import dp
from handlers.filters import GroupFilter
import logging


@dp.message(Command('schedule'), GroupFilter)
async def schedule_commands(message: Message):
    await message.reply(lx.SCHEDULE_NOT_AVAILABLE, parse_mode='MarkdownV2')
    await message.delete()
    logging.warning('schedule command in group chat')
    return
