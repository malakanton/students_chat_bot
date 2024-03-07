from aiogram.types import Message, CallbackQuery
import logging
from loguru import logger
import inspect
import sys


def setup_logging() -> None:
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            level: str | int
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.opt(depth=0, exception=record.exc_info).log(level, record.getMessage())
    logging.basicConfig(

        handlers=[
            logging.FileHandler(
                'bot_logs.log',
                mode='a'
            ),
            InterceptHandler()
        ],
        level='INFO',
        force=True
    )


def logging_msg(
        update: Message | CallbackQuery,
        logging_text: str = '',
) -> str:
    user_id = update.from_user.id
    chat_type, chat_id, command = '', '', ''
    if isinstance(update, Message):
        command = update.text
        chat_type = update.chat.type
        chat_id = update.chat.id
    elif isinstance(update, CallbackQuery):
        command = update.data
        chat_type = update.message.chat.type
        chat_id = update.message.chat.id
    return f'user_id: {user_id} chat_id: {chat_id} chat_type: {chat_type} command: {command} message: {logging_text}'
