from aiogram import Bot, Dispatcher
from models import Week
import config


bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher(bot)
week = Week(num=1)
print(week.__dict__)