import pandas as pd
import re
from config import LOGS_PATH, PATH, ADMIN_CHAT, LOGS_UPLOAD_TIME
from loader import bot
from aiogram.types.input_file import FSInputFile
from loader import db
import datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def parce_line(line: str) -> dict:
    timestamp = line.split('|')[0].split('.')[0].replace('T', ' ').strip()
    if not re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
        return dict()
    log_info = line.split('|')[-1].strip()
    log_fields = ['user_id', 'command', 'message', 'chat_id', 'chat_type']
    log_items = {
        'timestamp': timestamp
    }
    for field in log_fields:
        try:
            text = log_info.split(field + ':')[1]
            value = text.split()[0].strip()
            if field == 'message':
                value = text.strip()
        except IndexError:
            value = ''
        log_items[field] = value
    return log_items


def form_data(path: str = LOGS_PATH, dataframe = True) -> pd.DataFrame | list:
    with open(path, 'r') as file:
        lines = [line for line in file.readlines() if 'INFO' in line and ':emit:' not in line]
    data = []
    for line in lines:
        line_dict = parce_line(line)
        if line_dict:
            data.append(line_dict)
    df = pd.DataFrame(data)
    df = df[df.user_id != '']
    if dataframe:
        return df
    data = [
        (row['timestamp'],
         row['chat_id'],
         row['chat_type'],
         row['user_id'],
         row['command'],
         row['message']) for _, row in df.iterrows()
    ]
    return data


async def send_report(date: str, chat_id: int = ADMIN_CHAT):
    file_name = f'{PATH}logs_raw_report_{date}.xlsx'
    df = form_data()
    df.to_excel(file_name)
    file = FSInputFile(file_name)
    await bot.send_document(
        chat_id=chat_id,
        document=file
    )


async def upload_logs_to_db() -> None:
    today = str(dt.datetime.now() - dt.timedelta(hours=24))
    data = [
        row for row in form_data(dataframe=False)
        if row[0] >= today
    ]
    db.insert_logs(data)


def add_logs_scheduler(
        scheduler: AsyncIOScheduler,
        time: str = LOGS_UPLOAD_TIME
) -> None:
    hour, minute = list(map(int, time.split(':')))
    scheduler.add_job(
        upload_logs_to_db,
        trigger='cron',
        day_of_week='mon-sun',
        hour=hour,
        minute=minute
    )
