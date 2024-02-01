from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from loader import db, bot
import datetime as dt
from config import NOTIFICATIONS_ADVANCE
from lib.dicts import NotificationsAdvance
import lib.lexicon as lx
from lib.misc import prep_markdown


def cron_trigger(time: str, advance: int) -> tuple:
    delta = dt.timedelta(minutes=advance)
    time = dt.datetime.strptime(time, '%H:%M')
    trigger_time = (time - delta).time()
    return trigger_time.hour, trigger_time.minute


def add_scheduled_jobs(scheduler: AsyncIOScheduler, times: list):
    for time in times:
        for advance in NotificationsAdvance:
            hour, minute = cron_trigger(time, advance.value)
            scheduler.add_job(
                notify_users,
                args=[time, advance.value],
                trigger='cron',
                day_of_week='mon-fri',
                hour=hour,
                minute=minute)


async def notify_users(time: str, advance: int):
    date = dt.datetime.now().date()
    users_to_notify = db.get_users_lessons_notif(date, time, advance)
    for user, lesson in users_to_notify.items():
        await notify_user(user, lesson)
    logging.info(f'users notified: {len(users_to_notify)}')


async def notify_user(user_id, lesson):
    link = lx.NO_LINK_YET
    if lesson.link:
        link = f'[{lx.LINK_PHRASE}]<LINK>({lesson.link}<LINK>)'
    text = lx.NOTIF.format(
        minutes=NOTIFICATIONS_ADVANCE,
        subject=lesson.subj,
        teacher=lesson.teacher,
        start=lesson.start.strftime('%H:%M'),
        end=lesson.end.strftime('%H:%M'),
        link=link
    )
    await bot.send_message(user_id, text=prep_markdown(text))
