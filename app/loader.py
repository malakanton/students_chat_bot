from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lib.config.config import cfg
from db.db import DB
from google_api.google_calendar import GoogleCalendar
from google_api.google_drive import GoogleDriver
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from lib.misc import Lexicon
from lib.models.users import Users
from lib.schedule.schedule_client import ScheduleClient
from lib.s3 import S3Client
from loguru import logger
from openai import OpenAI


cfg.set_config()

bot = Bot(token=cfg.secrets.TG_TOKEN, parse_mode="MarkdownV2")

dp = Dispatcher()
logger.success("Telegram Bot and Dispatcher initialized successfully")

db = DB(
    host=cfg.secrets.HOST,
    user=cfg.USER,
    pg_pass=cfg.secrets.PG_PASS,
    db_name=cfg.DB_NAME,
    port=cfg.secrets.PORT,
)
logger.success("Postgres DB initialized successfully")

embeddings = OpenAIEmbeddings(
    base_url=cfg.OPEN_AI_URL, api_key=cfg.secrets.OPEN_AI_API_KEY
)

conn_str = cfg.CONN_STRING.format(
    host=cfg.secrets.HOST,
    port=cfg.secrets.PORT,
    user=cfg.USER,
    password=cfg.secrets.PG_PASS,
)

vector_db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name=cfg.INFO_COLLECTION,
    connection_string=conn_str,
)

subjects_vector_db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name=cfg.SUBJECTS_COLLECTION,
    connection_string=conn_str,
)

gpt_client = OpenAI(api_key=cfg.secrets.OPEN_AI_API_KEY, base_url=cfg.OPEN_AI_URL)
logger.success("OpenAI stuff initialized successfully")

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

users = Users()
users.update(db)

gc = GoogleCalendar(cfg.SCOPES, cfg.CREDS_PATH)
logger.success("Google Calendar initialized successfully")

gd = GoogleDriver(scopes=cfg.SCOPES, creds_path=cfg.CREDS_PATH, local_path=cfg.PATH)
logger.success("Google Driver initialized successfully")

s3 = S3Client()
logger.success("S3 Client initialized successfully")

lx = Lexicon("lexicon.yml")

schd = ScheduleClient(cfg.SCHEDULE_HOST, cfg.SCHEDULE_PORT)
logger.success("Schedule client initialised_successfully")
