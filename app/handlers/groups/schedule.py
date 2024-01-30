from aiogram.types import Message
from aiogram.filters import Command
from lib import lexicon as lx
from lib.misc import prep_markdown
from loader import dp
from handlers.filters import GroupFilter
import logging


@dp.message(Command('schedule'), GroupFilter)
async def schedule_commands(message: Message):
    logging.warning('schedule command in group chat')
    await message.reply(prep_markdown(lx.SCHEDULE_NOT_AVAILABLE))
    await message.delete()
    return
