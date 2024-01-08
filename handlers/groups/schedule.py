from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.callbacks import ScheduleCallback
from keyboards.schedule import schedule_kb
from lib import lexicon as lx
from loader import dp, bot
from lib.misc import get_today
from handlers.filters import group_filter
import logging


@dp.message(Command('schedule'), group_filter)
async def schedule_commands(message: Message):
    logging.warning('schedule command in group chat')
    return
    today = get_today()
    if not week.days:
        await message.answer(text=lx.NO_SCHEDULE)
    else:
        await message.answer(
            text=lx.SCHEDULE,
            parse_mode='html',
            reply_markup=await schedule_kb(today)
        )
    await message.delete()


@dp.callback_query(ScheduleCallback.filter())
async def callback_schedule(call: CallbackQuery, callback_data: ScheduleCallback):
    day_id = int(callback_data.day)
    day = week.get_day(day_id)
    print('day info', day)
    if not day:
        await call.answer(
            text=lx.NO_SCHEDULE,
            show_alert=True)
    elif day.free:
        await call.answer(
            text=lx.FREE_DAY,
            show_alert=True)
    else:
        await call.answer()
        schedule = day.schedule
        msg = lx.SCHEDULE_RESULTS.format(
            day_of_week=day.name,
            date=day.date
        )
        msg += form_schedule_text(schedule)
        await bot.send_message(
            text=msg,
            chat_id=call.message.chat.id)


def form_schedule_text(schedule: list) -> str:
    text = ''
    lessons_dict = {
        1: 'Одна пара',
        2: 'Две пары',
        3: 'Три пары',
        4: 'Четыре пары',
        5: 'Пять пар',
        6: 'Шесть пар'
    }
    lessons_num = len(schedule)
    text += lessons_dict[lessons_num] + '\n'
    for lesson in sorted(schedule, key=lambda x: x.start):
        start_time = lesson.start.strftime('%H:%M')
        end_time = lesson.end.strftime('%H:%M')
        text += f'{start_time}-{end_time} **{lesson.subj}**, {lesson.teacher} ({lesson.loc})\n'
    return text


# async def set_schedule(
#         filename: str,
#         new_week: models.Week
# ):
#     schedule, week_num = get_schedule(filename, GROUP)
#     print(schedule)
#     print(new_week.days)
#     for day in new_week.days.values():
#         for item in schedule:
#             if (
#                     day.name == item['day'] and
#                     item['subj'] != ''
#             ):
#                 day.date = str(item['start'].date())
#                 lesson = Lesson(
#                     subj=item['subj'],
#                     start=item['start'].to_pydatetime(),
#                     end=item['end'].to_pydatetime(),
#                     teacher=item['teacher'],
#                     loc=item['loc']
#                 )
#                 day.schedule.append(lesson)
#         if day.schedule:
#             day.free = False
#     print('week set:', new_week.__dict__)
#     return new_week