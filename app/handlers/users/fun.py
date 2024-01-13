from app.loader import dp
from aiogram.types import Message
from aiogram import F
from app.handlers.filters import UserFilter


@dp.message(UserFilter(),
            F.content_type == 'text',
            ~F.contains('/'))
async def set_date(message: Message):
    text = message.text
    user_id = message.from_user.id
    await message.answer('test')
