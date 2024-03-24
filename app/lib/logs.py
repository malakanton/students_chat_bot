from aiogram.types import Message, CallbackQuery
from logging.handlers import RotatingFileHandler
import logging
from loguru import logger


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
            InterceptHandler()
        ],
        level='INFO',
        force=True,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )
    logger.add(
        'logs/bot_logs.log',
        backtrace=True,
        rotation=10_000_000,
        diagnose=True,
        format='{time}|{level}|{name}:{function}:{line}|{message}'
    )


def logging_msg(
        update: Message | CallbackQuery,
        logging_text: str = '',
        command: str = ''
) -> str:
    user_id = update.from_user.id
    chat_type, chat_id = '', ''
    if isinstance(update, Message):
        if not command:
            command = update.text
        chat_type = update.chat.type
        chat_id = update.chat.id
    elif isinstance(update, CallbackQuery):
        if not command:
            command = update.data
        chat_type = update.message.chat.type
        chat_id = update.message.chat.id
    return f'user_id: {user_id} chat_id: {chat_id} chat_type: {chat_type} command: {command} message: {logging_text}'
