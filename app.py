from aiogram import executor
import handlers
import datetime
from loader import dp, bot
from config import ADMIN_ID


async def on_startup(_):
    print('Bot is active.')
    await bot.send_message(ADMIN_ID, f"Новый запуск: {str(datetime.datetime.now())}")


if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, on_startup=on_startup)

