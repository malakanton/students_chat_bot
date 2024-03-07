import os
from loguru import logger
from config import PATH
from aiogram import F
from lib import lexicon as lx
from lib.logs import logging_msg
from lib.misc import prep_markdown
from loader import db, bot, users
from handlers.routers import users_router
from handlers.filters import UserFilter
from aiogram.types import Message, CallbackQuery
from keyboards.file import schedule_exists_kb, file_kb
from keyboards.callbacks import FileCallback, LibCallback
from lib.misc import chat_msg_ids, valid_schedule_format
from keyboards.library import lib_type_kb, subjects_kb, confirm_subj_kb
from lib.schedule_uploader import upload_schedule
from lib.schedule_parser import ScheduleParser
from keyboards.buttons import FileButt, SchdUpdButt, Confirm, FileTypeButt


# обработка прикрепленных документов
# в личных сообщениях прикреплять документы могут только админы и старосты
@users_router.message(F.content_type == 'document',
            UserFilter(users.admins | users.heads))
async def document_processing(message: Message):
    logger.info(f'document uploaded in private chat {message.chat.id}')
    file = message.document
    db_file_id = db.add_file(
        file_name=file.file_name,
        uploaded_by=message.from_user.id,
        tg_file_id=file.file_id,
    )
    logger.info(f'file info uploaded: {db_file_id}')
    await message.reply(
        text=lx.FILE_ATTACHED.format(file.file_name),
        reply_markup=await file_kb(db_file_id),
        parse_mode='HTML'
    )


# если пользователь выбрал расписание
@users_router.callback_query(FileCallback.filter(F.file_type == FileButt.SCHEDULE.name))
async def schedule_choice(call: CallbackQuery, callback_data: FileCallback):
    action = callback_data.update
    logger.info(logging_msg(call))
    file_name, tg_file_id = db.update_file(
        file_id=callback_data.file_id,
        file_type=callback_data.file_type
    )
    if not valid_schedule_format(file_name):
        await call.answer(lx.NOT_SCHEDULE_FORMAT, show_alert=True)
        logger.info(f'file {file_name} doesnt pass the schedule test')
        return
    file = await bot.get_file(tg_file_id)
    schedule_path = PATH + file_name
    logger.info(f'schedule file path: {schedule_path}')
    await bot.download_file(
        file_path=file.file_path,
        destination=schedule_path
    )
    sp = ScheduleParser(schedule_path)
    week_num = sp.week_num
    if not sp.week_num:
        await call.answer(lx.DIDNT_PARSE, show_alert=True)
        logger.error(f'didnt manage to get schedule dates {schedule_path}!!!')
        return
    await call.answer()
    # если это первоначальная загрузка файла
    if action == 'init':
        # если расписание на эту неделю уже есть в бд
        existing_weeks = db.get_weeks()
        if week_num in existing_weeks:
            schedule_exists = existing_weeks.get(week_num)
            await call.message.edit_text(
                reply_markup=await schedule_exists_kb(callback_data.file_id),
                text=prep_markdown(
                    lx.SCHEDULE_EXISTS.format(
                    start=schedule_exists['start'],
                    end=schedule_exists['end'])
                )
            )
        else:
            await call.message.edit_text(prep_markdown(lx.FILE_SAVED.format('Расписания')))
            await bot.send_chat_action(call.chat.id, "typing")
            await upload_schedule(sp)
            await call.answer(text=lx.SCHEDULE_UPLOADED, show_alert=True)
            logger.info('schedule uploaded')
    # если пользователь выбрал обновить расписание
    elif action == SchdUpdButt.UPDATE.value:
        await bot.send_chat_action(call.chat.id, "typing")
        await upload_schedule(sp, update=True)
        await call.message.edit_text(lx.SCHEDULE_UPDATED)
        logger.info('schedule updated')
    # если пользователь выбрал не обновлять расписание
    elif action == SchdUpdButt.KEEP.value:
        await call.message.edit_text(lx.KEEP_SCHEDULE)
        logger.info('schedule keep as it was')
    os.remove(schedule_path)


# если пользователь выбрал учебные материалы, даем выбрать предмет
@users_router.callback_query(FileCallback.filter(F.file_type == FileButt.STUDY.name))
async def subj_choice(call: CallbackQuery, callback_data: FileCallback):
    logger.info(logging_msg(call))
    await call.answer()
    users_subjects = db.get_subjects_for_user_or_group(call.from_user.id)
    markup = await subjects_kb(users_subjects, callback_data.file_id)
    await call.message.edit_text(
        text=prep_markdown(lx.CHOOSE_SUBJ),
        reply_markup=markup
    )
    logger.debug('you are in study materials section')


# выбор типа материала
@users_router.callback_query(LibCallback.filter(F.type == 'None'))
async def choose_lib_type(call: CallbackQuery, callback_data: LibCallback):
    logger.info(logging_msg(call))
    await call.answer()
    markup = await lib_type_kb(callback_data.subject_id, callback_data.file_id)
    await call.message.edit_text(
        text=prep_markdown(lx.CHOOSE_TYPE),
        reply_markup=markup
    )

# подтверждение выбора
@users_router.callback_query(LibCallback.filter(F.confirm == 'None'))
async def choose_lib_type(call: CallbackQuery, callback_data: LibCallback):
    await call.answer()
    logger.info(logging_msg(call))
    markup = await confirm_subj_kb(callback_data.file_id,
                                   callback_data.subject_id,
                                   callback_data.type)
    subj_dict_inv = db.get_subjects_for_user_or_group(call.from_user.id, inverted=True)
    subj_name = subj_dict_inv[callback_data.subject_id]
    subj_type = FileTypeButt[callback_data.type].value
    msg = lx.CONFIRM_SUBJECT.format(subj_type.lower(), subj_name)
    await call.message.edit_text(
        text=msg,
        reply_markup=markup
    )


#сохранение если все ок, или откат назад если пользователь нажал отмена
@users_router.callback_query(LibCallback.filter(F.confirm != 'None'))
async def confirm_subj(call: CallbackQuery, callback_data: LibCallback):
    await call.answer()
    logger.info(logging_msg(call))
    if callback_data.confirm == Confirm.OK.name:
        file_name, tg_file_id = db.update_file(
            file_id=callback_data.file_id,
            file_type=callback_data.type,
            subj_id=callback_data.subject_id
        )
        subj_dict_inv = db.get_subjects_for_user_or_group(call.from_user.id, inverted=True)
        subj_name = subj_dict_inv[callback_data.subject_id]
        subj_type = FileTypeButt[callback_data.type].value
        msg = prep_markdown(lx.CONFIRM_SUBJECT_OK.format(subj_type, subj_name))
        await call.message.edit_text(msg)
    else:
        msg = prep_markdown(lx.FILE_ATTACHED.format(''))
        await call.message.edit_text(
            text=msg,
            reply_markup=await file_kb(callback_data.file_id)
        )


# если пользователь выбрал не сохранять
@users_router.callback_query(FileCallback.filter(F.file_type == FileButt.CANCEL.name))
async def dont_save_choice(call: CallbackQuery, callback_data: FileCallback):
    logger.info(logging_msg(call))
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer(lx.DIDNT_SAVE_FILE, show_alert=True)
    await bot.delete_message(
        chat_id=chat_id,
        message_id=msg_id)
