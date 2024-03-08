from openai import OpenAI
from loguru import logger
from aiogram import Bot, Dispatcher
from google_api.google_drive import GoogleDriver
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from google_api.google_calendar import GoogleCalendar
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from db.db import DB
from lib.misc import get_host_port
from lib.models import Groups, Users


bot = Bot(
    token=TG_TOKEN,
    parse_mode='MarkdownV2'
)
dp = Dispatcher()
logger.success('Telegram Bot and Dispatcher initialized successfully')
host, port = get_host_port()
db = DB(
    host=host,
    user=USER,
    pg_pass=PG_PASS,
    db_name=DB_NAME,
    port=port
)
logger.success('Postgres DB initialized successfully')
embeddings = OpenAIEmbeddings(
    base_url=OPEN_AI_URL,
    api_key=OPEN_AI_API_KEY
)
vector_db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name=COLLECTION,
    connection_string=CONN_STRING.format(host=host, port=port, user=USER, password=PG_PASS),
)
gpt_client = OpenAI(
    api_key=OPEN_AI_API_KEY,
    base_url=OPEN_AI_URL
)
logger.success('OpenAI stuff initialized successfully')
gr = Groups(db.get_groups())
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
users = Users(
    admins=db.get_users_ids('admin'),
    heads=db.get_users_ids('head'),
    regular=db.get_users_ids('regular'),
    unreg=db.get_users_ids('unreg')
)
gc = GoogleCalendar(
    SCOPES,
    CREDS_PATH
)
logger.success('Google Calendar initialized successfully')
gd = GoogleDriver(
    scopes=SCOPES,
    creds_path=CREDS_PATH,
    local_path=PATH
)
logger.success('Google Driver initialized successfully')


