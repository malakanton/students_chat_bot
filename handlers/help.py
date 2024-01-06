from aiogram.types import Message
from aiogram.filters import Command
import bot_replies as br
from loader import dp


@dp.message(Command('help'))
async def help_cmd(message: Message):
    # help_kb = kb(
    #     [
    #         '/help',
    #         '/start',
    #         '/schedule'
    #     ]
    # )
    await message.answer(text=br.HELP_MSG, parse_mode='html')
    # await send_message(message, f'{br.HELP_MSG}\n{br.COMPANYS_INFO}', kb=k.help_kb())
    await message.delete()
