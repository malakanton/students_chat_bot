import datetime as dt
from typing import Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.users.schedule import form_day_schedule_text
from lib.dicts import NotificationsAdvance
from lib.logs_report import add_logs_scheduler, send_report
from lib.misc import get_today, prep_markdown
from lib.models.lessons import Lesson
from loader import bot, db, lx, schd
from lib.config.config import cfg
from loguru import logger


def set_scheduler(scheduler: AsyncIOScheduler):
    add_scheduled_jobs(scheduler, cfg.LESSONS_TIMINGS)
    add_report_scheduler(scheduler)
    add_logs_scheduler(scheduler)
    add_daily_push_notification_jobs(scheduler)


def cron_trigger(time: str, advance: int) -> tuple:
    delta = dt.timedelta(minutes=advance)
    time = dt.datetime.strptime(time, "%H:%M")
    trigger_time = (time - delta).time()
    return trigger_time.hour, trigger_time.minute


def add_scheduled_jobs(scheduler: AsyncIOScheduler, times: list):
    for time in times:
        for advance in NotificationsAdvance:
            hour, minute = cron_trigger(time, advance.value)
            scheduler.add_job(
                notify_users,
                args=[time, advance.value],
                trigger="cron",
                day_of_week="mon-fri",
                hour=hour,
                minute=minute,
            )


def add_report_scheduler(
    scheduler: AsyncIOScheduler, time: str = cfg.LOGS_REPORT_TIME
) -> None:
    hour, minute = list(map(int, time.split(":")))
    date = str(dt.datetime.now().date())
    scheduler.add_job(
        send_report,
        args=[date],
        trigger="cron",
        day_of_week="sun",
        hour=hour,
        minute=minute,
    )


async def notify_users(time: str, advance: int):
    date = str(dt.datetime.now().date())
    users_to_notify = db.get_users_with_advance_notif(advance)

    for user in users_to_notify:
        lessons = schd.get_group_daily_lessons(user.group_id, date)

        for lesson in lessons:
            if lesson.start.strftime('%h:%m') == time:
                await notify_user(user, lesson, advance)

    logger.info(f"users notified: {len(users_to_notify)}")


async def notify_user(user_id: int, lesson: Lesson, advance: int) -> None:
    link = lx.NO_LINK_YET
    if lesson.link:
        link = f"[{lx.LINK_PHRASE}]<LINK>({lesson.link}<LINK>)"
    text = lx.NOTIF.format(
        minutes=advance,
        subject=lesson.subj,
        teacher=lesson.teacher,
        start=lesson.start.strftime("%H:%M"),
        end=lesson.end.strftime("%H:%M"),
        link=link,
    )
    await bot.send_message(user_id, text=prep_markdown(text))


async def form_schedule_text(user_id: int) -> str:
    text = ""
    today = get_today()
    user = db.get_user(user_id)
    week = schd.get_group_weekly_lessons(user.group_id, today.week)

    if week:
        schedule_text = await form_day_schedule_text(week.get_day(today.day_of_week))
        text = (
            prep_markdown(lx.MORNING_SCHEDULE)
            + schedule_text
            + prep_markdown(lx.MORNING_GREETING)
        )

    return text


async def daily_push(user_id: int) -> None:
    text = await form_schedule_text(user_id)

    if text:
        await bot.send_message(user_id, text=text)
        logger.info(f"Send daily notification to user {user_id}")


def add_daily_push_for_user(
    user_id: int, time: Union[dt.datetime.time, str], scheduler: AsyncIOScheduler
) -> None:

    job_id = str(user_id)
    job = scheduler.get_job(job_id)

    if isinstance(time, str):
        time = dt.datetime.strptime(time, "%H:%M")

    if job:
        job.reschedule(trigger="cron", hour=time.hour, minute=time.minute)
    else:
        scheduler.add_job(
            daily_push,
            args=[user_id],
            trigger="cron",
            day_of_week="mon-fri",
            hour=time.hour,
            minute=time.minute,
            id=job_id,
        )


def add_daily_push_notification_jobs(scheduler: AsyncIOScheduler):

    users_to_notify = db.get_users_push_time()

    for user_id, time in users_to_notify.items():
        add_daily_push_for_user(user_id, time, scheduler)
