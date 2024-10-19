import asyncio
from typing import List

from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from handlers.routers import users_router
from keyboards.buttons import ScheduleButt
from keyboards.callbacks import ScheduleCallback
from keyboards.schedule import schedule_kb
from lib.dicts import LESSONS_DICT, MONTHS
from lib.logs import logging_msg
from lib.misc import chat_msg_ids, get_today, prep_markdown
from lib.models.lessons import DayOfWeek, Week, Lesson
from loader import bot, db, logger, lx, schd
from lib.config.config import cfg
from handlers.filters import IsTeacher


@users_router.message(Command("schedule"), IsTeacher())
async def schedule_commands(message: Message):

    logger.info(logging_msg(message, "teacher schedule command in private chat"))
    user = db.get_user(message.from_user.id)
    today = get_today()

    week_num = today.week
    day_of_week = today.day_of_week
    week = schd.get_teacher_weekly_lessons(user.teacher_id, week_num)

    if not week:
        await message.answer(prep_markdown(lx.NO_SCHEDULE))
    else:

        if day_of_week == 7:
            text = await form_week_schedule_text(week)

        else:
            text = lx.SCHEDULE + await form_day_schedule_text(week.get_day(day_of_week))

        await message.answer(
            text=text,
            reply_markup=await schedule_kb(week, day_of_week),
            disable_web_page_preview=True,
        )

    chat_id, msg_id = message.chat.id, message.message_id
    await message.delete()
    await hide_keyboard(chat_id, msg_id)


# если выбрал день
@users_router.callback_query(
    ScheduleCallback.filter(~F.command.in_(ScheduleButt._member_names_)),
    IsTeacher()
)
async def day_chosen(call: CallbackQuery, callback_data: ScheduleCallback):
    await call.answer()

    logger.info(logging_msg(call))
    user_id, msg_id = chat_msg_ids(call)
    user = db.get_user(user_id)

    week = schd.get_teacher_weekly_lessons(user.teacher_id, callback_data.week)
    day_num = int(callback_data.command)
    text = await form_day_schedule_text(week.get_day(day_num))

    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, day_num),
        disable_web_page_preview=True,
    )


# если выбрал всю неделю
@users_router.callback_query(
    ScheduleCallback.filter(F.command == ScheduleButt.WEEK.name),
    IsTeacher()
)
async def week_chosen(call: CallbackQuery, callback_data: ScheduleCallback):
    await call.answer()
    logger.info(logging_msg(call))
    user_id, msg_id = chat_msg_ids(call)
    user = db.get_user(user_id)
    week = schd.get_teacher_weekly_lessons(user.teacher_id, callback_data.week)
    text = await form_week_schedule_text(week)
    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, 0),
        disable_web_page_preview=True,
    )


# если выбрал смену недели
@users_router.callback_query(
    ScheduleCallback.filter(
        F.command.in_({ScheduleButt.BACK.name, ScheduleButt.FORW.name})
    ),
    IsTeacher()
)
async def change_week(call: CallbackQuery, callback_data: ScheduleCallback):
    user_id, msg_id = chat_msg_ids(call)
    user = db.get_user(user_id)
    logger.info(logging_msg(call))
    if callback_data.command == ScheduleButt.BACK.name:
        week = schd.get_teacher_weekly_lessons(user.teacher_id, callback_data.week - 1)
        if not week:
            await call.answer(lx.NO_PREV_SCHEDULE, show_alert=True)
            return
    elif callback_data.command == ScheduleButt.FORW.name:
        week = schd.get_teacher_weekly_lessons(user.teacher_id, callback_data.week + 1)
        if not week:
            await call.answer(lx.NO_NEXT_SCHEDULE, show_alert=True)
            return
    else:
        await call.answer()
        week = schd.get_teacher_weekly_lessons(user.teacher_id, callback_data.week)
    text = await form_week_schedule_text(week)
    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, 0),
        disable_web_page_preview=True,
    )


async def form_week_schedule_text(week: Week):
    from_day = week.days[0].date
    to_day = week.days[-1].date
    text = lx.WEEK_SCHEDULE
    if from_day.month == to_day.month:
        text += f" *{from_day.day}* по *{to_day.day} {MONTHS[to_day.month]}*\n"
    else:
        text += f" *{from_day.day} {MONTHS[from_day.month]}* по *{to_day.day} {MONTHS[to_day.month]}*\n"
    days = week.get_all_active()
    for day in days:
        text += await form_day_schedule_text(day, single=False)
    text = prep_markdown(text)
    text = text.replace("<LINK>\\", "")
    return text


async def form_day_schedule_text(day: DayOfWeek, single=True) -> str:
    if single:
        text = f"🗓*{day.name}* {day.date.day} {MONTHS[day.date.month]}\n\n"
    else:
        text = f"\n__*{day.name}*__\n"
    if day.free:
        text += lx.FREE_DAY
    else:
        lessons = group_by_lesson_time(day.schedule)
        if single:
            text += LESSONS_DICT.get(len(lessons), '') + "\n\n"

        for lesson in lessons:
            start_time = lesson.start.strftime("%H:%M")
            end_time = lesson.end.strftime("%H:%M")
            num = f'*№{lesson.num}* ' if lesson.num else ''

            if lesson.comment:
                text += f"❗️**{lesson.comment.upper()}**❗️\n"
            lesson_text = f"{num}*{start_time}*-*{end_time}* \n{lesson.subj}, _{lesson.group_name}_ "

            if lesson.loc:
                lesson_text += f"({lesson.loc})"

            if lesson.cancelled:
                lesson_text = f"~{lesson_text}~"

            text += lesson_text + '\n\n'

    if single:
        text = prep_markdown(text)
    return text


def group_by_lesson_time(lessons: List[Lesson]) -> List[Lesson]:
    lessons = sorted(lessons, key=lambda lesson: lesson.start)
    grouped_lessons = []

    for i, lesson in enumerate(lessons):
        if i == 0:
            grouped_lessons.append(lesson)
            continue

        if lesson.start == grouped_lessons[-1].start and lesson.subj == grouped_lessons[-1].subj:
            grouped_lessons[-1].group_name += ', ' + lesson.group_name
        else:
            grouped_lessons.append(lesson)

    return grouped_lessons


async def hide_keyboard(chat_id, message_id):
    await asyncio.sleep(cfg.SCHEDULE_KB_TIMEOUT)
    await bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id + 1, reply_markup=None
    )
    logger.info("hide schedule kb")
