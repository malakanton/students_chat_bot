from aiogram import types
from aiogram.dispatcher.filters import Command
from keyboards.keyboards import schedule_kb, schedule_cb
import bot_replies as br
from loader import dp, week, bot
from lib.misc import get_today


@dp.message_handler(Command('schedule'))
async def schedule_commands(message: types.Message):
    today = get_today()
    if not week.days:
        await message.answer(text=br.NO_SCHEDULE)
    else:
        await message.answer(
            text=br.SHEDULE,
            parse_mode='html',
            reply_markup=schedule_kb(today)
        )
    await message.delete()
    # print(week)
    # await message.answer(text=week.mon.schedule)
    # await message.delete()


@dp.callback_query_handler(schedule_cb.filter())
async def callback_schedule(call: types.CallbackQuery, callback_data: dict):
    # await call.answer()
    day_id = int(callback_data['day'])
    day = week.get_day(day_id)
    print('day info', day)
    if not day:
        await call.answer(
            text=br.NO_SCHEDULE,
            show_alert=True)
    elif day.free:
        await call.answer(
            text=br.FREE_DAY,
            show_alert=True)
    else:
        await call.answer()
        schedule = day.schedule
        msg = br.SHEDULE_RESULTS.format(
            day_of_week=day.name,
            date=day.date
        )
        msg += form_schedule_text(schedule)
        await bot.send_message(
            text=msg,
            chat_id=call.message.chat.id)


    # await bot.send_message(text=week.mon.schedule, chat_id=call.message.chat.id)


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
