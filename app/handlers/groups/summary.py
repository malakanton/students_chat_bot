import logging
from lib import lexicon as lx
from aiogram.types import Message
from aiogram.filters import Command
from loader import dp, bot
from handlers.filters import GroupFilter
from lib.misc import prep_markdown, logging_msg
from gpt.chat_summary import gpt_summary


@dp.message(Command('summary'), GroupFilter)
async def summary_request(message: Message):
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
