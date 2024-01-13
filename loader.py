from aiogram import Bot, Dispatcher
from lib.models import Groups, Users
from db import DB
import config
from config import HOST, USER, PG_PASS, DB_NAME


bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher()
db = DB(host=HOST, user=USER, pg_pass=PG_PASS, db_name=DB_NAME)
gr = Groups(db.get_groups())
users = Users(
    admins=db.get_users_ids('admin'),
    heads=db.get_users_ids('head'),
    regular=db.get_users_ids('regular'),
    unreg=db.get_users_ids('unreg')
)
print(users)

