import asyncio
from main_menu import set_menu
from config import LESSONS_TIMINGS
from loader import dp, bot, scheduler
from lib.logs import setup_logging
from lib.logs_report import add_logs_scheduler
from lib.notifications import add_scheduled_jobs, add_report_scheduler
from handlers.routers import users_router, groups_router


async def main():
    setup_logging()
    dp.include_routers(users_router, groups_router)
    add_scheduled_jobs(scheduler, LESSONS_TIMINGS)
    add_report_scheduler(scheduler)
    add_logs_scheduler(scheduler)
    scheduler.start()
    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
