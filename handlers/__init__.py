from aiogram import types

def send_message(message: types.Message, text: str, kb=None):
    return message.answer(text=text, parse_mode='html', reply_markup=kb)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    hello_msg = f'Hello, <b>{message.from_user.first_name}</b>!\n{br.DESCRIPTION}'
    await send_message(message, hello_msg)
    await bot.send_sticker(message.chat.id, sticker=br.HELLO_STICKER)
    await message.delete()