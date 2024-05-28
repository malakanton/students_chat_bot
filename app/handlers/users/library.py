import os

from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import FSInputFile
from config import PATH
from handlers.routers import users_router
from keyboards.buttons import CancelButt
from keyboards.callbacks import LibCallback
from keyboards.library import choose_file_kb, lib_type_kb, subjects_kb
from lib.logs import logging_msg
from lib.misc import prep_markdown
from lib.models import File
from loader import bot, db, s3, users, lx
from loguru import logger


@users_router.message(Command("library"))
@users_router.callback_query(
    LibCallback.filter((F.file_id == -1) & (F.confirm == CancelButt.BACK.name))
)
async def library(message: Message | CallbackQuery):
    """Reaction to /library command -> return the keyboard with
    a subjects list"""
    logger.info(logging_msg(message))

    if isinstance(message, CallbackQuery):
        message = message.message

    files = db.list_files(message.from_user.id)
    subjects = {file.subj_name: file.subj_id for file in files}

    markup = await subjects_kb(subjects)
    await message.answer(text=prep_markdown(lx.LIB_CHOOSE_SUBJ), reply_markup=markup)
    await message.delete()


# выбор типа материала
@users_router.callback_query(LibCallback.filter((F.file_id == -1) & (F.type == "None")))
async def choose_lib_type(call: CallbackQuery, callback_data: LibCallback):
    """Reacts to subject button ang let to choose the
    file type
    """
    logger.info(logging_msg(call))
    await call.answer()

    user_id = call.from_user.id
    files = db.list_files(user_id)
    file_types = filter_file_types(user_id, callback_data, files)

    markup = await lib_type_kb(
        callback_data.subject_id, chosen_types=file_types, back=True
    )
    await call.message.edit_text(
        text=prep_markdown(lx.LIB_CHOOSE_TYPE), reply_markup=markup
    )


@users_router.callback_query(
    LibCallback.filter((F.file_id == -1) & (F.type != "None") & (F.confirm == "None"))
)
async def choose_file(call: CallbackQuery, callback_data: LibCallback):
    """Get the list of available files to download"""
    logger.info(logging_msg(call))
    await call.answer()

    files = await get_files_list(call.from_user.id, callback_data)

    markup = await choose_file_kb(files)
    subject_name = files[0].subj_name

    await call.message.edit_text(
        text=prep_markdown(lx.LIB_FILES_LIST.format(subject_name)), reply_markup=markup
    )


@users_router.callback_query(
    LibCallback.filter((F.file_id == -1) & (F.confirm.isdigit()))
)
async def download_file(call: CallbackQuery, callback_data: LibCallback):
    """Upload the choosen file to chat"""
    logger.info(logging_msg(call))
    await call.answer()

    files = await get_files_list(call.from_user.id, callback_data)
    file_to_download = files[int(callback_data.confirm)]

    await send_file_to_chat(file_to_download, call)


async def get_files_list(user_id: int, callback_data: LibCallback) -> list[File]:
    """Get the files list from db and filter according to
    choosen subject and type and type"""
    all_files_for_user = db.list_files(user_id)
    files = list(
        filter(
            lambda t: t.file_type == callback_data.type
            and t.subj_id == callback_data.subject_id,
            all_files_for_user,
        )
    )
    return sorted(files, key=lambda file: file.file_name)


async def send_file_to_chat(file: File, call: CallbackQuery) -> None:
    """Send file to chat"""
    chat_id = call.message.chat.id
    path_download_to = os.path.join(PATH, file.file_name)

    if s3.download_file(file.s3_path, path_download_to):
        await bot.send_chat_action(chat_id, "upload_document")
        file_for_bot = FSInputFile(path_download_to)
        await bot.send_document(chat_id=chat_id, document=file_for_bot)
        logger.info(
            logging_msg(call, f"Successfully sent file {file.s3_path}", "send_file")
        )
        os.remove(path_download_to)
    else:
        await bot.send_message(
            chat_id, lx.LIB_FAILED_TO_DOWNLOAD.format(file.file_name), parse_mode="HTML"
        )
        logger.warning(f"Failed to send file {file.s3_path} to user {chat_id}")


def filter_file_types(
    user_id: int, callback_data: LibCallback, files: list
) -> list[str]:
    file_types = [
        file.file_type
        for file in files
        if file.subj_id == int(callback_data.subject_id)
    ]

    if user_id not in users.allowed:
        file_types = [f_type for f_type in file_types if f_type not in {"HOMEWORK"}]

    return file_types
