from aiogram.types import Message, CallbackQuery
import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(
                'bot_logs.log',
                mode='a'
            ),
            logging.StreamHandler()
        ]
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
