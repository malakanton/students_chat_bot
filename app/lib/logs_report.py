import pandas as pd
import re
from config import LOGS_PATH, ADMIN_ID, PATH
from loader import bot
from aiogram.types.input_file import FSInputFile


def parce_line(line: str) -> dict:
    timestamp = re.search(r'\[.*\]', line).group(0)[1:-1].split(',')[0]
    log_info = line.split('root')[1].replace('-', '').strip()
    log_fields = ['user_id', 'command', 'message', 'chat_id','chat_type']
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


def form_dataframe(path: str = LOGS_PATH) -> pd.DataFrame:
    with open(path, 'r') as file:
        lines = [line for line in file.readlines() if 'root' in line]
    data = []
    for line in lines:
        data.append(
            parce_line(line)
        )
    return pd.DataFrame(data)


async def send_report(date: str):
    file_name = f'{PATH}report_{date}.xlsx'
    df = form_dataframe()
    df.to_excel(file_name)
    file = FSInputFile(file_name)
    await bot.send_document(
        chat_id=ADMIN_ID,
        document=file
    )

# import os
# send_report('2024-02-03')