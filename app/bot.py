import asyncio
import logging
from main_menu import set_menu
from config import LESSONS_TIMINGS
from loader import dp, bot, scheduler
# from lib.notifications import add_scheduled_jobs


async def main():
    from handlers import dp
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    # add_scheduled_jobs(scheduler, LESSONS_TIMINGS)
    # scheduler.start()
    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



