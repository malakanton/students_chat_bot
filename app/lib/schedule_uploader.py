from loguru import logger
from loader import db, gc
from lib.models import Group
from lib.dicts import RU_DAYS, PERMANENT_LINKS
from google_api.google_calendar import GoogleCalendar
from lib.schedule_parser import ScheduleParser, ScheduleFilter


async def upload_schedule(sp: ScheduleParser, update=False) -> None:
    try:
        df = sp.get_schedule()
        groups = db.get_groups()
        su = ScheduleUploader(sp.week_num, gc)
        sf = ScheduleFilter(df, groups)
        sf.extract_groups_schedules()
    except:
        logger.error(f'Didnt manage to parse {sp.filename}')
        return
    if update:
        db.erase_existing_schedule(sp.week_num)
    logger.info(f'Start uploading schedules')
    for group in groups:
        schedule = sf.get_group_schedule(group.name)
        await su.upload_group_schedule(schedule, group)
        if group.course == 1:
            await su.add_to_google(schedule, group.name, update)


class ScheduleUploader:
    week_num: int
    teachers: dict
    subjects: dict
    gc: GoogleCalendar

    def __init__(self, week_num: int, gc: GoogleCalendar):
        self.gc = gc
        self.week_num = week_num
        self.teachers = db.get_teachers()
        self.subjects = db.get_subjects()

    def _check_teacher(self, teacher: str):
        """If teacher not in db, then add a new teacher"""
        if teacher not in self.teachers:
            self.teachers = db.add_teacher(teacher)
            logger.info(f'New teacher added: {teacher}')
        return self.teachers.get(teacher)

    def _check_subject(self, subject_code: str, subject):
        """If subject not in db, then add a new subject"""
        if subject_code not in self.subjects:
            self.subjects = db.add_subject(subject_code, subject)
            logger.info(f'New subject added: {subject}')
        return self.subjects.get(subject_code)

    async def add_to_google(
            self,
            schedule: list[dict],
            group_name: str,
            update: bool=False
    ) -> None:
        """Uploads or updates a schedule to google calendar"""
        logger.info(f'Start uploading to google for {group_name}')
        if update:
            await self.gc.update_schedule(schedule, group_name)
        else:
            await self.gc.upload_schedule(schedule, group_name)
        logger.info(f'Finished upload to google for {group_name}')

    async def upload_group_schedule(
            self,
            schedule: list[dict],
            group: Group
    ) -> None:
        for lesson in schedule:
            subj_code = lesson.get('subj_code', '')
            subject = lesson.get('subj', '')
            teacher = lesson.get('teacher', '')
            if (
                    not subj_code or
                    not subject
            ):
                continue
            teacher_id = self._check_teacher(teacher)
            subj_id = self._check_subject(subj_code, subject)
            db.add_lesson(
                week_num=self.week_num,
                day=RU_DAYS.get(lesson['day'], 1),
                date=str(lesson['start'].to_pydatetime().date()),
                start=str(lesson['start'].to_pydatetime().time()),
                end=str(lesson['end'].to_pydatetime().time()),
                group_id=group.id,
                subj_id=subj_id,
                teacher_id=teacher_id,
                loc=lesson.get('loc', ''),
                link=PERMANENT_LINKS.get(teacher_id, None)
            )
        logger.info(f'Uploaded schedule to db for group {group.name}')
