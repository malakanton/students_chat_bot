from environs import Env

env = Env()
env.read_env()

TG_TOKEN = env.str('TG_TOKEN')
ADMIN_ID = env.str('ADMIN_ID')
PATH = './temp/'
GROUP = 'ИСП11-123ВПоз'