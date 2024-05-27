from environs import Env

env = Env()
env.read_env()
# telegram
TG_TOKEN = env.str("TG_TOKEN")
ADMIN_ID = env.str("ADMIN_ID")
ADMIN_IDS = env.list("ADMIN_IDS")
ADMIN_CHAT = env.str("ADMIN_CHAT")
# basic
PATH = "./temp/"
LOGS_PATH = "./logs/bot_logs.log"
GROUP = "ИСП11-123ВПоз"
UNAUTHORIZED_GROUP_TIMOUT = 60
SCHEDULE_KB_TIMEOUT = 15 * 60
NOTIFICATIONS_ADVANCE = 15
# scheduler
LOGS_REPORT_TIME = "12:00"
LOGS_UPLOAD_TIME = "00:00"
LESSONS_TIMINGS = ["17:00", "18:40"]
TZ = env.str("TZ")
# db
HOST_LOCAL = env.str("HOST")
PORT_LOCAL = "5433"
HOST = "pg_db_container"
PORT = "5432"
USER = "postgres"
PG_PASS = env.str("PG_PASS")
DB_NAME = "students_bot_db"
# Google
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]
FORM_ID = "1sDsXgKFbf2D5WasvMXmx6h9s60wLlLQQOLDW021Cg_A"
CREDS_PATH = "./google_api/studentsbot-414221-88a1d65d3976.json"
# OpenAI
RAG_FILES_DIR = "gpt/temp/"
CHATS_HISTORY = "./chats_history/chat_history{}.txt"
MESSAGES_TO_KEEP = 200
OPEN_AI_API_KEY = env.str("OPEN_AI_API_KEY")
OPEN_AI_URL = "https://api.proxyapi.ru/openai/v1"
BLABLA_MODEL = "gpt-4o"
# SUMMARY_MODEL = 'gpt-3.5-turbo-1106'
SUMMARY_MODEL = "gpt-4o"
CONN_STRING = "postgresql+psycopg2://{user}:{password}@{host}:{port}/vector_db"
SUBJECTS_COLLECTION = "subjects"
INFO_COLLECTION = "subjects_info"
SUBJ_CLF_TH = 0.25
# S3
S3_KEY_ID = env.str("S3_KEY_ID")
S3_SECRET = env.str("S3_SECRET")
S3_ENDPOINT = "https://storage.yandexcloud.net"
S3_BUCKET = env.str("BUCKET")
