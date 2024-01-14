import logging
from aiogram import F
from loader import dp
from aiogram.types import Message
from handlers.filters import GroupFilter


@dp.message(GroupFilter,
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


