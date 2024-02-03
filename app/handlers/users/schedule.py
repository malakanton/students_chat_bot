import asyncio
import logging
from aiogram import F
from lib import lexicon as lx
from loader import dp, db, bot
from aiogram.filters import Command
from lib.models import DayOfWeek, Week
from config import SCHEDULE_KB_TIMEOUT
from handlers.filters import UserFilter
from lib.dicts import LESSONS_DICT, MONTHS
from keyboards.schedule import schedule_kb
from keyboards.buttons import ScheduleButt
from aiogram.types import Message, CallbackQuery
from keyboards.callbacks import ScheduleCallback
from lib.misc import (get_today,
                    chat_msg_ids,
                    prep_markdown,
                    test_users_dates,
                    logging_msg)


@dp.message(Command('schedule'), UserFilter())
async def schedule_commands(message: Message):
    logging.info(logging_msg(message, 'schedule command in private chat'))
    user_id = message.from_user.id
    today = get_today(test_users_dates.get(user_id, None))
    week_num = today.week
    day_of_week = today.day_of_week
    week = db.get_schedule(user_id, week_num)
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
            disable_web_page_preview=True
        )
    chat_id, msg_id = message.chat.id, message.message_id
    await message.delete()
    await hide_keyboard(chat_id, msg_id)


# если выбрал день
@dp.callback_query(ScheduleCallback.filter(~F.command.in_(ScheduleButt._member_names_)))
async def day_chosen(call: CallbackQuery, callback_data: ScheduleCallback):
    await call.answer()
    logging.info(logging_msg(call))
    user_id, msg_id = chat_msg_ids(call)
    week = db.get_schedule(user_id, callback_data.week)
    day_num = int(callback_data.command)
    text = await form_day_schedule_text(week.get_day(day_num))
    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, day_num),
        disable_web_page_preview=True
    )


# если выбрал всю неделю
@dp.callback_query(ScheduleCallback.filter(F.command == ScheduleButt.WEEK.name))
async def week_chosen(call: CallbackQuery, callback_data: ScheduleCallback):
    await call.answer()
    logging.info(logging_msg(call))
    user_id, msg_id = chat_msg_ids(call)
    week = db.get_schedule(user_id, callback_data.week)
    text = await form_week_schedule_text(week)
    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, 0),
        disable_web_page_preview=True
    )


# если выбрал смену недели
@dp.callback_query(ScheduleCallback.filter(F.command.in_({ScheduleButt.BACK.name,
                                                          ScheduleButt.FORW.name})))
async def change_week(call: CallbackQuery, callback_data: ScheduleCallback):
    user_id, msg_id = chat_msg_ids(call)
    logging.info(logging_msg(call))
    if callback_data.command == ScheduleButt.BACK.name:
        week = db.get_schedule(user_id, callback_data.week - 1)
        if not week:
            await call.answer(lx.NO_PREV_SCHEDULE, show_alert=True)
            return
    elif callback_data.command == ScheduleButt.FORW.name:
        week = db.get_schedule(user_id, callback_data.week + 1)
        if not week:
            await call.answer(lx.NO_NEXT_SCHEDULE, show_alert=True)
            return
    else:
        await call.answer()
        week = db.get_schedule(user_id, callback_data.week)
    text = await form_week_schedule_text(week)
    await call.message.edit_text(
        text=text,
        reply_markup=await schedule_kb(week, 0),
        disable_web_page_preview=True
    )


async def form_week_schedule_text(week: Week):
    from_day = week.days[0].date
    to_day = week.days[-1].date
    text = lx.WEEK_SCHEDULE
    if from_day.month == to_day.month:
        text += f'*{from_day.day}* по *{to_day.day} {MONTHS[to_day.month]}*\n'
    else:
        text += f'*{from_day.day} {MONTHS[from_day.month]}* по *{to_day.day} {MONTHS[to_day.month]}*\n'
    days = week.get_all_active()
    for day in days:
        text += await form_day_schedule_text(day, single=False)
    text = prep_markdown(text)
    text = text.replace('<LINK>\\', '')
    return text


async def form_day_schedule_text(day: DayOfWeek, single=True) -> str:
    if single:
        text = f'🗓*{day.name}* {day.date.day} {MONTHS[day.date.month]}\n\n'
    else:
        text = f'\n__*{day.name}*__\n'
    if day.free:
        text += lx.FREE_DAY
    else:
        lessons_num = len(day.schedule)
        if single:
            text += LESSONS_DICT[lessons_num] + '\n\n'
        for lesson in sorted(day.schedule, key=lambda lesson: lesson.start):
            start_time = lesson.start.strftime('%H:%M')
            end_time = lesson.end.strftime('%H:%M')
            text += f'*{start_time}*-*{end_time}* **{lesson.subj}**, {lesson.teacher} '
            if lesson.link and day.id != 6:
                text += f'📺️[LINK]<LINK>({lesson.link}<LINK>)\n'
            else:
                text += f'({lesson.loc})\n'
    if single:
        text = prep_markdown(text)
    return text


async def hide_keyboard(chat_id, message_id):
    await asyncio.sleep(SCHEDULE_KB_TIMEOUT)
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id+1, reply_markup=None)
    logging.info('hide schedule kb')
