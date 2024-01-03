from aiogram import types
import bot_replies as br
import loader
import os
import models
from loader import dp
from config import PATH, GROUP
from keyboards.keyboards import file_kb, file_cb
from lib.calendar_parser import get_schedule
from models import Lesson


@dp.message_handler(content_types=['document'])
async def document_processing(message: types.Message):
    file = message.document
    file_id = 1
    file_name = file['file_name']
    msg = br.FILE_ATTACHED.format(filename=file_name)
    await file.download(destination_file=PATH + file_name)
    await message.reply(text=msg, parse_mode='html', reply_markup=file_kb(file_id))




@dp.callback_query_handler(file_cb.filter(file_type='schedule'))
async def callback_schedule(call: types.CallbackQuery, callback_data: dict):
    call.answer()
    file_id = callback_data['file_id']
    latest_file_path = latest_file(PATH)
    week = await set_schedule(latest_file_path, loader.week)
    await loader.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=br.FILE_SAVED.format(saved_to='Расписания'))
    await call.answer(text="Расписание загружено", show_alert=True)


@dp.callback_query_handler(file_cb.filter(file_type='study_file'))
async def callback_file(call: types.CallbackQuery, callback_data: dict):
    cbd = call.data
    latest_file_path = latest_file(PATH)
    print('you are in study materials section')
    print(cbd)
    await call.answer()


def latest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


async def set_schedule(
        filename: str,
        new_week: models.Week
):
    schedule = get_schedule(filename, GROUP)
    print(schedule)
    print(new_week.days)
    for day in new_week.days.values():
        for item in schedule:
            if (
                    day.name == item['day'] and
                    item['subj'] != ''
            ):
                day.date = str(item['start'].date())
                lesson = Lesson(
                    subj=item['subj'],
                    start=item['start'].to_pydatetime(),
                    end=item['end'].to_pydatetime(),
                    teacher=item['teacher'],
                    loc=item['loc']
                )
                day.schedule.append(lesson)
        if day.schedule:
            day.free = False
    print('week set:', new_week.__dict__)
    return new_week


# set_schedule('../temp/Очно_заочное_отделение_с_2_10_по_07_10.pdf', week)