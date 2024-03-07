from loguru import logger
from lib import lexicon as lx
from aiogram.types import Message
from aiogram.filters import Command
from loader import bot
from handlers.routers import groups_router
from lib.misc import prep_markdown
from lib.logs import logging_msg
from gpt.chat_summary import gpt_summary


@groups_router.message(Command('summary'))
async def summary_request(message: Message):
    logger.info(logging_msg(message, 'summary command in group chat'))
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, "typing")
    gpt_summary_text = await gpt_summary(chat_id)
    if gpt_summary:
        await message.answer(
            prep_markdown(gpt_summary_text)
        )
    else:
        await message.answer(
            prep_markdown(lx.NO_SUMMARY)
        )
    await message.delete()
