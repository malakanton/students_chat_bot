from loader import dp, db
from aiogram.types import Message, CallbackQuery
from aiogram import F
from handlers.filters import UserFilter,LessonLinkFilter
from lib import lexicon as lx
from lib.misc import prep_markdown, get_today
from keyboards.lesson_link import link_kb
from keyboards.callbacks import LessonLinkCallback

LINK = ''


@dp.message(UserFilter(), LessonLinkFilter())
async def link_detected(message: Message, link: str):
    today = get_today()
    msg_id = message.message_id
    lessons = db.get_future_two_days(message.from_user.id, str(today.date))
    markup = await link_kb(lessons, msg_id)
    await message.reply(
        text='looks like a link',
        reply_markup=markup
    )


@dp.callback_query(LessonLinkCallback())
async def update_lesson_link(call: CallbackQuery, callback_data: LessonLinkCallback):
    if callback_data.subj_id == 0:
        await call.answer()
        await call.message.delete()
    else:
        return
