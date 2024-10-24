from aiogram.filters import Command
from aiogram.types import Message
from handlers.routers import users_router
from handlers.filters import IsTeacher
from lib.logs import logging_msg
from lib.misc import prep_markdown
from loader import db, lx
from loguru import logger


@users_router.message(Command("help"))
async def help_cmd(message: Message):
    logger.info(logging_msg(message, "help command in private chat"))
    help_msg = prep_markdown(lx.HELP_MSG)
    await message.answer(text=help_msg)
    await message.delete()


@users_router.message(Command("description"), IsTeacher())
async def desc_cmd(message: Message):
    logger.info(logging_msg(message, "teacher description command in private chat"))
    desc_msg = prep_markdown(lx.DESCRIPTION_FOR_TEACHERS)
    await message.answer(text=desc_msg)
    await message.delete()


@users_router.message(Command("description"))
async def desc_cmd(message: Message):
    logger.info(logging_msg(message, "description command in private chat"))
    gc_link = db.get_user_group(message.from_user.id)[2]
    if not gc_link:
        gc_link = "https://calendar.google.com/"
    desc_msg = prep_markdown(lx.DESCRIPTION.format(gc_link))
    await message.answer(text=desc_msg, disable_web_page_preview=True)
    await message.delete()


@users_router.message(Command("contacts"))
async def contacts_cmd(message: Message):
    logger.trace(logging_msg(message, "contacts command in private chat"))
    desc_msg = prep_markdown(lx.CONTACTS)
    await message.answer(text=desc_msg)
    await message.delete()
