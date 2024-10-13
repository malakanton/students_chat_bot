from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from handlers.routers import users_router
from loader import lx, schd
from lib.config.config import cfg
from keyboards.teachers import teachers_list_kb


@users_router.message(
    Command("teachers_code"), F.chat.id == int(cfg.secrets.ADMIN_ID)
)
async def get_teachers_list(message: Message):
    teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.name)
    markup = await teachers_list_kb(teachers, 0)
    await message.answer(
        text=lx.TEACHERS_LIST,
        reply_markup=markup
    )
    await message.delete()


# @users_router.callback_query(TeachersCallback.filter(F.id < 0))
# async def paginate(callback: CallbackQuery, callback_data: TeachersCallback):
#     await callback.answer()
#     teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.name)
#     index = callback_data.index
#     if callback_data.paginate == TeachersButt.RIGHT.name:
#         if index + TEACHERS_PER_PAGE < len(teachers):
#             index += TEACHERS_PER_PAGE
#
#     if callback_data.paginate == TeachersButt.LEFT.name:
#         if index - TEACHERS_PER_PAGE >= 0:
#             index -= TEACHERS_PER_PAGE
#
#     markup = await teachers_list_kb(teachers, index)
#
#     await callback.message.edit_reply_markup(
#         reply_markup=markup
#     )


# @users_router.callback_query(TeachersCallback.filter(F.id > 0))
# async def teacher_choosen(call: CallbackQuery, callback_data: TeachersCallback):
#     await call.answer()
#
#     teacher = schd.get_teachers(int(callback_data.id))
#
#     await bot.send_message(
#         chat_id=call.message.chat.id,
#         text=prep_markdown(lx.CODE_SENT.format(teacher.name, teacher.code))
#     )
