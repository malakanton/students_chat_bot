from aiogram import types
from aiogram.dispatcher.filters import Command
import bot_replies as br
from loader import dp, bot


@dp.message_handler(Command('start'))
async def start(message: types.Message):
    hello_msg = f'Hello, <b>{message.from_user.first_name}</b>!\n'
    hello_msg += br.DESCRIPTION
    await message.answer(text=hello_msg, parse_mode='html')
    await bot.send_sticker(message.chat.id, sticker=br.HELLO_STICKER)
    await message.delete()

