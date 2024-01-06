from aiogram.types import BotCommand
from aiogram import Bot
from loader import dp, bot
from config import ADMIN_ID
import logging


async def set_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/help',
                   description='про бота'),
        BotCommand(command='/schedule',
                   description='расписание'),
        BotCommand(command='/materials',
                   description='учебные материалы')
    ]
    await bot.set_my_commands(main_menu_commands)


if __name__ == '__main__':
    from handlers import dp
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(set_menu)
    # executor.start_polling(dp, on_startup=on_startup)
    dp.run_polling(bot)

