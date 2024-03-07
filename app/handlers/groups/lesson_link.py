import re
from loguru import logger
from loader import db
from aiogram.types import Message, CallbackQuery
from handlers.filters import LessonLinkFilter
from handlers.routers import groups_router
from lib import lexicon as lx
from lib.misc import prep_markdown, get_today
from keyboards.lesson_link import link_kb
from keyboards.callbacks import LessonLinkCallback


@groups_router.message(LessonLinkFilter())
async def link_detected(message: Message, link: str):
    logger.info('link detected')
    today = get_today()
    msg_id = message.message_id
    lessons = db.get_future_two_days(message.from_user.id, str(today.date))
    markup = await link_kb(lessons, msg_id)
    await message.reply(
        text=prep_markdown(lx.LINK_POSTED),
        reply_markup=markup
    )


@groups_router.callback_query(LessonLinkCallback.filter())
async def update_lesson_link(call: CallbackQuery, callback_data: LessonLinkCallback):
    if callback_data.subj_id == 0:
        await call.answer()
        await call.message.delete()
    else:
        try:
            link = re.findall(LessonLinkFilter().pattern,
                              call.message.reply_to_message.text)[0]
        except IndexError:
            return
        print('LINK: ', link)
        date = callback_data.date
        time = callback_data.time.replace('$', ':')
        subj_id = callback_data.subj_id
        db.update_link(date, time, subj_id, link)
        logger.info(f'link updated for dt {date} {time} subject {subj_id}, link {link}')
        await call.answer(lx.LINK_UPDATED, show_alert=True)
        await call.message.delete()
