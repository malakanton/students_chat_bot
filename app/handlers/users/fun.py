from loader import dp
from aiogram.types import Message
from aiogram import F
from handlers.filters import UserFilter
from lib import lexicon as lx
from lib.misc import prep_markdown


@dp.message(UserFilter(),
            F.content_type == 'text',
            ~F.contains('/'))
async def set_date(message: Message):
    text = message.text
    user_id = message.from_user.id
    answer = prep_markdown(lx.TEXT_REPLY)
    await message.answer(answer)
