from aiogram import types
import bot_replies as br
import os
import models
from lib.misc import chat_msg_ids
from loader import dp, db, bot
from config import PATH
import keyboards.keyboards as kb
from lib.calendar_parser import get_schedule, filter_df
from models import Lesson, ru_days


@dp.message_handler(content_types=['document'])
async def document_processing(message: types.Message):
    file = message.document
    file_id = 1
    file_name = file['file_name']

    msg = br.FILE_ATTACHED.format(filename=file_name)
    await file.download(destination_file=PATH + file_name)
    await message.reply(text=msg, parse_mode='html', reply_markup=kb.file_kb(file_id))


@dp.callback_query_handler(kb.file_cb.filter(file_type='schedule'))
async def callback_schedule(call: types.CallbackQuery, callback_data: dict):
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer()
    latest_file_path = latest_file(PATH)
    df, week_num, schedule_exists = await process_schedule_file(latest_file_path)
    if schedule_exists:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=kb.schedule_exists_kb(),
            text=br.SHEDULE_EXISTS.format(
                start=schedule_exists['start'],
                end=schedule_exists['end']
            )
        )
    else:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=br.FILE_SAVED.format(saved_to='Расписания'))
        await upload_schedule(df, week_num)
        await call.answer(text="Расписание загружено", show_alert=True)


@dp.callback_query_handler(kb.sch_exists_cb.filter())
async def callback_file(call: types.CallbackQuery, callback_data: dict):
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer()
    if callback_data['update'] == 'yes':
        latest_file_path = latest_file(PATH)
        df, week_num, _ = await process_schedule_file(latest_file_path)
        db.erase_existing_schedule(week_num)
        await upload_schedule(df, week_num)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text='Обновил расписание')
    else:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text='Расписание оставил как было')


@dp.callback_query_handler(kb.file_cb.filter(file_type='study_file'))
async def callback_file(call: types.CallbackQuery, callback_data: dict):
    latest_file_path = latest_file(PATH)
    print('you are in study materials section')
    await call.answer('not able to process study materials yet..', show_alert=True)


def latest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


async def process_schedule_file(filename:str):
    df, week_num = get_schedule(filename)
    weeks = db.get_weeks()
    schedule_exists = None
    if week_num in weeks:
        schedule_exists = weeks.get(week_num)
    return df, week_num, schedule_exists


async def upload_schedule(df, week_num):
    groups = db.get_groups()
    for group_id, group_name in groups.items():
        print(group_name)
        try:
            schedule = filter_df(df, group_name).to_dict(orient='records')
        except:
            print('error!!!')
            break
        print(schedule)
        upload_group_schedule(schedule, week_num, group_id)


def upload_group_schedule(
        schedule: list,
        week_num: int,
        group_id: int
):
    teachers = db.get_teachers()
    subjects = db.get_subjects()
    for lesson in schedule:
        subj_code = lesson.get('subj_code', '')
        subject = lesson.get('subj', '')
        teacher = lesson.get('teacher', '')
        if (
                not subj_code or
                not subject
        ):
            continue
        if teacher not in teachers:
            db.add_teacher(teacher)
            print(f'New teacher added: {teacher}')
            teachers = db.get_teachers()
        if subj_code not in subjects:
            db.add_subject(subj_code, subject)
            print(f'New subject added: {subject}')
            subjects = db.get_subjects()
        start = str(lesson['start'].to_pydatetime().time())
        end = str(lesson['end'].to_pydatetime().time())
        date = str(lesson['start'].to_pydatetime().date())
        db.add_lesson(
            week_num=week_num,
            day=ru_days.get(lesson['day'], 1),
            date=date,
            start=start,
            end=end,
            group_id=group_id,
            subj_id=subjects.get(subj_code, 0),
            teacher_id=teachers.get(teacher, 0),
            loc=lesson.get('loc', '')
        )
        print('lesson added')

# process_schedule('../temp/Очно_заочное_отделение_с_9_10_по_14_10_копия.pdf')
