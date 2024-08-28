from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from gpt.vector_db import DocumentsHandler
from handlers.routers import users_router
from langchain_community.document_loaders import TextLoader
from lib.misc import prep_markdown
from loader import bot, conn_str, embeddings, gd, vector_db, lx, schd
from lib.config.config import cfg
from loguru import logger
from keyboards.teachers import teachers_list_kb
from keyboards.callbacks import TeachersCallback
from aiogram.types import CallbackQuery



@users_router.message(
    Command("teachers_code"), F.chat.id == int(cfg.secrets.ADMIN_ID)
)
async def get_teachers_list(message: Message):
    teachers = schd.get_teachers()

    markup = await teachers_list_kb(teachers)
    await message.answer(
        text=lx.TEACHERS_LIST,
        reply_markup=markup
    )
    await message.delete()


@users_router.callback_query(TeachersCallback.filter())
async def teacher_choosen(call: CallbackQuery, callback_data: TeachersCallback):
    await call.answer()

    teacher = schd.get_teachers(int(callback_data.id))

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=prep_markdown(lx.CODE_SENT.format(teacher.name, teacher.code))
    )
