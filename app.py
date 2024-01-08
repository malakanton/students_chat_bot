from loader import dp, bot
import asyncio
from main_menu import set_menu
import logging
from config import PATH, ADMIN_IDS

async def main():
    from handlers import dp
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



