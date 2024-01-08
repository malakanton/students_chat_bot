from environs import Env

env = Env()
env.read_env()

TG_TOKEN = env.str('TG_TOKEN')
ADMIN_ID = env.str('ADMIN_ID')
ADMIN_IDS = env.list('ADMIN_IDS')
PATH = './temp/'
GROUP = 'ИСП11-123ВПоз'

HOST = '127.0.0.1'
USER = 'postgres'
PG_PASS = env.str('PG_PASS')
DB_NAME = 'students_bot_db'
