from environs import Env

env = Env()
env.read_env()
# telegram
TG_TOKEN = env.str('TG_TOKEN')
ADMIN_ID = env.str('ADMIN_ID')
ADMIN_IDS = env.list('ADMIN_IDS')
ADMIN_CHAT = env.str('ADMIN_CHAT')
# basic
PATH = './temp/'
LOGS_PATH = './bot_logs.log'
GROUP = 'ИСП11-123ВПоз'
UNAUTHORIZED_GROUP_TIMOUT = 60
SCHEDULE_KB_TIMEOUT = 15 * 60
NOTIFICATIONS_ADVANCE = 15
LOGS_REPORT_TIME = '12:00'
LESSONS_TIMINGS = ['17:00', '18:40']
TZ = env.str('TZ')
# db
HOST_LOCAL = '51.250.109.13'
PORT_LOCAL = '5433'
HOST = 'pg_db_container'
PORT = '5432'
USER = 'postgres'
PG_PASS = env.str('PG_PASS')
DB_NAME = 'students_bot_db'
# Google
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDS_PATH = './lib/studentsbot-414221-88a1d65d3976.json'
# OpenAI
CHATS_HISTORY = './chats_history/chat_history{}.txt'
MESSAGES_TO_KEEP = 100
OPEN_AI_API_KEY = env.str('OPEN_AI_API_KEY')
OPEN_AI_URL = 'https://api.proxyapi.ru/openai/v1'
MODEL = 'gpt-3.5-turbo-1106' #"gpt-3.5-turbo"
