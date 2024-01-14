from environs import Env

env = Env()
env.read_env()

TG_TOKEN = env.str('TG_TOKEN')
ADMIN_ID = env.str('ADMIN_ID')
ADMIN_IDS = env.list('ADMIN_IDS')
ADMIN_CHAT = env.str('ADMIN_CHAT')
PATH = './temp/'
GROUP = 'ИСП11-123ВПоз'
UNAUTHORIZED_GROUP_TIMOUT = 60
SCHEDULE_KB_TIMEOUT = 15 * 60

HOST = 'pg_db_container'
PORT = '5432'
USER = 'postgres'
PG_PASS = env.str('PG_PASS')
DB_NAME = 'students_bot_db'
