from db.db import DB
from lib.misc import get_host_port
from aiogram import Bot, Dispatcher
from lib.models import Groups, Users
from config import USER, PG_PASS, DB_NAME, TG_TOKEN, TZ
from apscheduler.schedulers.asyncio import AsyncIOScheduler


bot = Bot(
    token=TG_TOKEN,
    parse_mode='MarkdownV2'
)
dp = Dispatcher()
host, port = get_host_port()

db = DB(
    host=host,
    user=USER,
    pg_pass=PG_PASS,
    db_name=DB_NAME,
    port=port
)
gr = Groups(db.get_groups())
# scheduler = AsyncIOScheduler(timezone=TZ)
users = Users(
    admins=db.get_users_ids('admin'),
    heads=db.get_users_ids('head'),
    regular=db.get_users_ids('regular'),
    unreg=db.get_users_ids('unreg')
)


