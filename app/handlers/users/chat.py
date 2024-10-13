from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from gpt.rag import gpt_respond, gpt_teacher_respond
from handlers.routers import users_router
from handlers.filters import IsTeacher
from lib.logs import logging_msg
from lib.misc import prep_markdown
from loader import bot
from loguru import logger


@users_router.message(
    ~F.text.startswith("/"), ~F.text.startswith("#"), F.content_type == "text",
    IsTeacher()
)
async def bot_reply_to_teacher(message: Message):
    chat_id = message.chat.id
    logger.info(logging_msg(message, message.text, "$ask"))
    await bot.send_chat_action(chat_id, "typing")
    raw_answer = gpt_teacher_respond(message.text)
    answer = prep_markdown(raw_answer)
    logger.info(logging_msg(message, answer, "$gpt_respond"))

    try:
        await message.answer(answer)
    except TelegramBadRequest:
        await message.answer(raw_answer, parse_mode=None)


@users_router.message(
    ~F.text.startswith("/"), ~F.text.startswith("#"), F.content_type == "text"
)
async def bot_reply(message: Message):
    chat_id = message.chat.id
    logger.info(logging_msg(message, message.text, "$ask"))
    await bot.send_chat_action(chat_id, "typing")
    raw_answer = gpt_respond(message.text)
    answer = prep_markdown(raw_answer)
    logger.info(logging_msg(message, answer, "$gpt_respond"))

    try:
        await message.answer(answer)
    except TelegramBadRequest:
        await message.answer(raw_answer, parse_mode=None)


def prep_link(text: str) -> str:
    splitted_text = text.split()
    for i, word in enumerate(splitted_text):
        if "https://" in word:
            if word.endswith(".") or word.endswith("!"):
                word = word[:-2]
            if not (word.startswith("[") and word.endswith(")")):
                link = word.replace("\\", "")
                word = f"[{word}]({link})"
            else:
                word = word.replace("\\", "")
                for i, char in enumerate(word):
                    if char == ".":
                        word = word[:i] + "\\" + word[i:]
                    elif char == "]":
                        break
            splitted_text[i] = word
    return " ".join(splitted_text)
