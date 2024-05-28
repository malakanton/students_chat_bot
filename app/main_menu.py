from aiogram import Bot
from aiogram.types import BotCommand
from loader import lx


async def set_menu(bot: Bot):
    main_menu = []
    for command, description in lx.MAIN_MENU.items():
        main_menu.append(
            BotCommand(command=command, description=description),
        )
    await bot.set_my_commands(main_menu)
