from loader import dp, bot
import asyncio
from main_menu import set_menu
import logging
import datetime


async def main():
    from handlers import dp
    print("System time in Python app:", datetime.datetime.now())
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



