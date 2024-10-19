from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from handlers.routers import groups_router
from keyboards.buttons import TeachersButt
from keyboards.callbacks import TeachersCallback
from keyboards.teachers import teachers_list_kb, TEACHERS_PER_PAGE
from handlers.users.teachers_schedule import form_week_schedule_text
from lib.misc import get_today, prep_markdown
from loader import bot, cfg, schd
from aiogram import F


@groups_router.message(Command("teacher_schedule"), F.chat.id == int(cfg.secrets.ADMIN_CHAT))
async def teachers_list(message: Message):

    teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.last_name)

    await message.answer(
        text='Выбери препода',
        reply_markup=await teachers_list_kb(teachers, 0),
    )
    await message.delete()


@groups_router.callback_query(TeachersCallback.filter(F.id < 0),
                              F.message.chat.id == int(cfg.secrets.ADMIN_CHAT))
async def paginate(callback: CallbackQuery, callback_data: TeachersCallback):
    await callback.answer()

    teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.last_name)
    index = callback_data.index
    if callback_data.paginate == TeachersButt.RIGHT.name:
        if index + TEACHERS_PER_PAGE < len(teachers):
            index += TEACHERS_PER_PAGE

    if callback_data.paginate == TeachersButt.LEFT.name:
        if index - TEACHERS_PER_PAGE >= 0:
            index -= TEACHERS_PER_PAGE

    markup = await teachers_list_kb(teachers, index)

    await callback.message.edit_reply_markup(
        reply_markup=markup
    )


@groups_router.callback_query(TeachersCallback.filter(F.id > 0),
                              F.message.chat.id == int(cfg.secrets.ADMIN_CHAT))
async def post_teachers_schedule(callback: CallbackQuery):
    await callback.answer()
    callback_data = TeachersCallback.unpack(callback.data)

    await callback.message.delete()

    teacher = schd.get_teachers(callback_data.id)

    today = get_today()
    week = schd.get_teacher_weekly_lessons(callback_data.id, today.week)

    text = prep_markdown(f'Расписание для {teacher.last_name} {teacher.initials}\n')
    text += await form_week_schedule_text(week)

    await bot.send_message(text=text, chat_id=int(cfg.secrets.ADMIN_CHAT))
