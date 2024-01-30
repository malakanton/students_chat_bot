import re
import logging
from loader import dp, db
from aiogram.types import Message, CallbackQuery
from handlers.filters import LessonLinkFilter, GroupFilter
from lib import lexicon as lx
from lib.misc import prep_markdown, get_today
from keyboards.lesson_link import link_kb
from keyboards.callbacks import LessonLinkCallback


@dp.message(GroupFilter, LessonLinkFilter())
async def link_detected(message: Message, link: str):
    logging.info('link detected')
    today = get_today()
    msg_id = message.message_id
    lessons = db.get_future_two_days(message.from_user.id, str(today.date))
    print(link)
    markup = await link_kb(lessons, msg_id)
    await message.reply(
        text=prep_markdown(lx.LINK_POSTED),
        reply_markup=markup
    )


@dp.callback_query(LessonLinkCallback.filter())
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
        logging.info(f'link updated for dt {date} {time} subject {subj_id}, link {link}')
        await call.answer(lx.LINK_UPDATED, show_alert=True)
        await call.message.delete()
