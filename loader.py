from aiogram import Bot, Dispatcher
from lib.models import Groups
from db import DB
import config
from config import HOST, USER, PG_PASS, DB_NAME


bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher()
db = DB(host=HOST, user=USER, pg_pass=PG_PASS, db_name=DB_NAME)
gr = Groups(db.get_groups())

