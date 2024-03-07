from aiogram.types import Message
from aiogram.filters import Command
from loader import db, bot
from lib import lexicon as lx
from handlers.routers import groups_router
from lib.models import DayOfWeek, Week
from lib.dicts import LESSONS_DICT, MONTHS
from loguru import logger
from handlers.users.schedule import form_day_schedule_text

from lib.misc import (get_today,
                      chat_msg_ids,
                      prep_markdown,
                      test_users_dates)


@groups_router.message(Command('schedule'))
async def schedule_commands(message: Message):
    logger.warning('schedule command in group chat')
    chat_id = message.chat.id
    today = get_today()
    week_num = today.week
    day_of_week = today.day_of_week
    week = db.get_schedule(chat_id, week_num)
    if not week:
        await message.answer(prep_markdown(lx.NO_SCHEDULE))
    else:
        schedule_text = await form_day_schedule_text(
                                    week.get_day(day_of_week)
        )
        text = lx.SCHEDULE + schedule_text + '\n' + prep_markdown(lx.SCHEDULE_FOR_DETAIL)
        await message.answer(
            text=text,
            disable_web_page_preview=True
        )
    await message.delete()
