from loader import db
from lib.schedule_parser import get_schedule, filter_df
from lib.dicts import RU_DAYS, PERMANENT_LINKS
import logging


async def process_schedule_file(filename: str):
    try:
        df, week_num = get_schedule(filename)
    except:
        logging.error(f'didnt manage to get schedule from {filename}!!!')
        return None, None, None
    weeks = db.get_weeks()
    schedule_exists = None
    if week_num in weeks:
        schedule_exists = weeks.get(week_num)
    return df, week_num, schedule_exists


async def upload_schedule(df, week_num):
    groups = db.get_groups()
    not_uploaded_groups = []
    for group in groups:
        if group.name in df.columns:
            try:
                schedule = filter_df(df, group.name).to_dict(orient='records')
            except:
                logging.warning(f'error!!! while filtering group {group.name}')
                break
            await upload_group_schedule(schedule, week_num, group.id)
        else:
            not_uploaded_groups.append(group)


async def upload_group_schedule(
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
            logging.info(f'New teacher added: {teacher}')
            teachers = db.get_teachers()
        if subj_code not in subjects:
            db.add_subject(subj_code, subject)
            logging.info(f'New subject added: {subject}')
            subjects = db.get_subjects()
        start = str(lesson['start'].to_pydatetime().time())
        end = str(lesson['end'].to_pydatetime().time())
        date = str(lesson['start'].to_pydatetime().date())
        teacher_id = teachers.get(teacher, 0)
        db.add_lesson(
            week_num=week_num,
            day=RU_DAYS.get(lesson['day'], 1),
            date=date,
            start=start,
            end=end,
            group_id=group_id,
            subj_id=subjects.get(subj_code, 0),
            teacher_id=teacher_id,
            loc=lesson.get('loc', ''),
            link=PERMANENT_LINKS.get(teacher_id, None)
        )