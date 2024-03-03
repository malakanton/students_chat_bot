from aiogram.types import Message
from aiogram.filters import Command
from lib import lexicon as lx
from lib.misc import prep_markdown
from handlers.routers import groups_router
import logging


@groups_router.message(Command('schedule'))
async def schedule_commands(message: Message):
    logging.warning('schedule command in group chat')
    print('check')
    await message.reply(prep_markdown(lx.SCHEDULE_NOT_AVAILABLE))
    await message.delete()
    return
