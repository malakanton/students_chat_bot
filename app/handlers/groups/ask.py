from loguru import logger
from loader import bot
from aiogram.types import Message
from aiogram.filters import Command
from lib.misc import prep_markdown
from gpt.rag import gpt_respond
from aiogram.exceptions import TelegramBadRequest
from handlers.routers import users_router, groups_router
from lib.logs import logging_msg


@groups_router.message(
            Command('ask')
            )
async def gpt_reply(message: Message):
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, "typing")
    user_query = message.text.replace('/ask', '').strip()
    logger.info(logging_msg(message, user_query, '$ask'))
    raw_answer = gpt_respond(user_query)
    answer = prep_markdown(raw_answer)
    if 'https://' in answer:
        answer = prep_link(answer)
    logger.info(logging_msg(message, answer, '$gpt_respond'))
    try:
        await message.answer(answer)
    except TelegramBadRequest:
        await message.answer(
            raw_answer,
            parse_mode=None
        )


def prep_link(text: str) -> str:
    splitted_text = text.split()
    for i, word in enumerate(splitted_text):
        if 'https://' in word:
            if word.endswith('.') or word.endswith('!'):
                word = word[:-2]
            if not (
                word.startswith('[') and
                word.endswith(')')
            ):
                link = word.replace('\\', '')
                word = f"[{word}]({link})"
            else:
                word = word.replace('\\', '')
                for i, char in enumerate(word):
                    if char == '.':
                        word = word[:i] + '\\' + word[i:]
                    elif char ==']':
                        break
            splitted_text[i] = word
    return ' '.join(splitted_text)
