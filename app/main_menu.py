from aiogram import Bot
from aiogram.types import BotCommand
from lib.lexicon import MAIN_MENU


async def set_menu(bot: Bot):
    main_menu = []
    for command, description in MAIN_MENU.items():
        main_menu.append(
            BotCommand(command=command, description=description),
        )
    await bot.set_my_commands(main_menu)
