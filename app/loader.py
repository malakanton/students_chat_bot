from db.db import DB
from lib.misc import get_host_port
from aiogram import Bot, Dispatcher
from lib.models import Groups, Users
from openai import OpenAI
from config import USER, PG_PASS, DB_NAME, TG_TOKEN, OPEN_AI_API_KEY, OPEN_AI_URL
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lib.google_calendar import GoogleCalendar
from config import SCOPES, CREDS_PATH
from loguru import logger


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
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
users = Users(
    admins=db.get_users_ids('admin'),
    heads=db.get_users_ids('head'),
    regular=db.get_users_ids('regular'),
    unreg=db.get_users_ids('unreg')
)
gpt_client = OpenAI(
    api_key=OPEN_AI_API_KEY,
    base_url=OPEN_AI_URL
)
gc = GoogleCalendar(SCOPES, CREDS_PATH)
logger.success('All Tools initialized successfully')

