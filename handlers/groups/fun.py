from loader import dp, db, bot
from aiogram.types import Message
from handlers.filters import group_filter
from aiogram import F
import logging


@dp.message(group_filter,
            F.content_type != 'document')
async def fun_handler(message: Message):
    # print(message.chat.id)
    # print(message.message_id)
    # print(message.__dict__)
    # print(f'https://t.me/c/{message.chat.id}/{message.message_id}')
    logging.info('message received')


# file_id = 'BQACAgIAAxkBAAIDFmWYVeMQAvgXkaDIWSMUBJXXN-hoAAI5SgAC0gPBSImhtAESU0PQNAQ'
# file = await bot.get_file(file_id)
# print(file.__dict__)


