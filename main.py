from aiogram import Bot, executor, Dispatcher
from config import *
from handlers import *

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


async def on_startup(_):
    print('Bot is active.')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
