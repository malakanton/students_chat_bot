from aiogram import types
from aiogram.dispatcher.filters import Command
from keyboards.keyboards import kb
import bot_replies as br
from loader import dp


@dp.message_handler(Command('help'))
async def help_cmd(message: types.Message):
    help_kb = kb(
        [
            '/help',
            '/start',
            '/schedule',
            '/description'
        ]
    )
    await message.answer(text=br.HELP_MSG, parse_mode='html', reply_markup=help_kb)
    # await send_message(message, f'{br.HELP_MSG}\n{br.COMPANYS_INFO}', kb=k.help_kb())
    await message.delete()
