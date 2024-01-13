from loader import dp, db, bot
from aiogram.types import Message
from aiogram import F
from handlers.filters import UserFilter
import logging
from lib.misc import test_users_dates
import re
import datetime as dt


@dp.message(UserFilter,
            F.content_type == 'text',
            F.text.lower().startswith('today'))
async def set_date(message: Message):
    text = message.text
    user_id = message.from_user.id
    try:
        numbers = re.findall(r'\d{2}', text)[::-1]
        date = '2024-' + '-'.join(numbers)
        date = dt.datetime.strptime(date, '%Y-%m-%d')
        test_users_dates[user_id] = date
        print(test_users_dates)
        await message.reply(f'Установил текущаю дату {date.date()}')
        logging.info(f'user {user_id} set a new today date {date}')
    except ValueError:
        await message.reply(f"введи нормальную дату, а не {text.replace('today', '')} (сначала день потом месяц)")



# @dp.message(user_filter,
#             F.content_type == 'text',
#             ~F.text.startswith('/'))
# async def fun_handler(message: Message):
#     print(message.__repr__)
#     print(message.chat.id)
#     print(message.message_id)
#     print(message.__dict__)
#     print(f'https://t.me/c/{message.chat.id}/{message.message_id}')
#     logging.info('message received')


# file_id = 'BQACAgIAAxkBAAIDFmWYVeMQAvgXkaDIWSMUBJXXN-hoAAI5SgAC0gPBSImhtAESU0PQNAQ'
# file = await bot.get_file(file_id)
# print(file.__dict__)


