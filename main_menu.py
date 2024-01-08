from aiogram.types import BotCommand
from aiogram import Bot


async def set_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/help',
                   description='❔ про бота'),
        BotCommand(command='/schedule',
                   description='📅 посмотреть расписание'),
        BotCommand(command='/library',
                   description='📚 учебные материалы')
    ]
    await bot.set_my_commands(main_menu_commands)