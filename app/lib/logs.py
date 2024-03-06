from aiogram.types import Message, CallbackQuery
import logging
from loguru import logger
import inspect
import sys


def setup_logging() -> None:
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(filename)s:%(lineno)d #%(levelname)-8s '
    #            '[%(asctime)s] - %(name)s - %(message)s',
    #     handlers=[
    #         logging.FileHandler(
    #             'bot_logs.log',
    #             mode='a'
    #         ),
    #         logging.StreamHandler()
    #     ]
    # )
    # class InterceptHandler(logging.Handler):
    #     def emit(self, record):
    #         level = logger.level(record.levelname).name
    #         logger.log(level, record.getMessage(), format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
    #
    # # logger.remove()
    # logging.getLogger('aiogram').setLevel(logging.DEBUG)
    # logging.getLogger('aiogram').addHandler(InterceptHandler())
    # logging.getLogger('asyncio').setLevel(logging.DEBUG)
    # logging.getLogger('asyncio').addHandler(InterceptHandler())
    # class PropagateHandler(logging.Handler):
    #     def emit(self, record: logging.LogRecord) -> None:
    #         logging.getLogger(record.name).handle(record)
    #
    # logger.add(PropagateHandler(), format="{message}")
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            level: str | int
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.opt(depth=0, exception=record.exc_info).log(level, record.getMessage())
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=0,
        force=True
    )
    # logger.add('logs / logs.log', level='TRACE', format="{time} {level} {message}")
    # logger.add(sys.stderr, level='TRACE', format="{time} {level} {message}")


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
