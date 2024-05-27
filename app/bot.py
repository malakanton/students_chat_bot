import asyncio

from handlers.routers import groups_router, users_router
from lib.logs import setup_logging
from lib.notifications import set_scheduler
from loader import bot, dp, scheduler
from loguru import logger
from main_menu import set_menu


@logger.catch()
async def main():
    setup_logging()
    dp.include_routers(users_router, groups_router)

    set_scheduler(scheduler)

    scheduler.start()

    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Bot polling starting...")
    await dp.start_polling(bot)
    logger.success("Bot polling stopped")


if __name__ == "__main__":
    asyncio.run(main())
