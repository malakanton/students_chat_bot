import asyncio

from handlers.routers import groups_router, users_router
from lib.logs import setup_logging
from lib.notifications import set_scheduler
from loader import bot, dp, scheduler, cfg
from loguru import logger
from main_menu import set_menu
import uvicorn
from api import http_app


@logger.catch()
async def start_bot():
    setup_logging()
    dp.include_routers(users_router, groups_router)

    set_scheduler(scheduler)

    scheduler.start()

    await set_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Bot polling starting...")
    await dp.start_polling(bot)
    logger.success("Bot polling stopped.")


async def start_fastapi():
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s | %(levelname)s | %(message)s"
    config = uvicorn.Config(http_app, host=cfg.SELF_HOST, port=cfg.SELF_PORT, log_level="info", log_config=log_config)
    server = uvicorn.Server(config)
    logger.success("Uvicorn start server")
    await server.serve()


async def main():
    await asyncio.gather(
        start_bot(),
        start_fastapi(),
    )


if __name__ == "__main__":
    asyncio.run(main())
