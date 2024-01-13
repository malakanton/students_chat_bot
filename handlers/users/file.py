import os
import logging
from aiogram.types import Message, CallbackQuery
from config import PATH
from aiogram import F
from lib import lexicon as lx
from loader import dp, db, bot, users
from handlers.filters import UserFilter
from keyboards.file import schedule_exists_kb, file_kb
from keyboards.callbacks import FileCallback, LibCallback
from keyboards.library import lib_type_kb, subjects_kb, confirm_subj_kb
from lib.misc import chat_msg_ids, valid_schedule_format
from lib.schedule_uploader import process_schedule_file, upload_schedule
from keyboards.buttons import FileButt, SchdUpdButt, Confirm, FileTypeButt


# обработка прикрепленных документов
# в личных сообщениях прикреплять документы могут только админы и старосты
@dp.message(F.content_type == 'document',
            UserFilter(users.admins | users.heads))
async def document_processing(message: Message):
    logging.info(f'document uploaded in private chat {message.chat.id}')
    file = message.document
    db_file_id = db.add_file(
        file_name=file.file_name,
        uploaded_by=message.from_user.id,
        tg_file_id=file.file_id,
    )
    logging.info(f'file info uploaded: {db_file_id}')
    await message.reply(
        text=lx.FILE_ATTACHED.format(file.file_name),
        reply_markup=await file_kb(db_file_id)
    )


# если пользователь выбрал расписание
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.SCHEDULE.name))
async def schedule_choice(call: CallbackQuery, callback_data: FileCallback):
    action = callback_data.update
    file_name, tg_file_id = db.update_file(
        file_id=callback_data.file_id,
        file_type=callback_data.file_type
    )
    file = await bot.get_file(tg_file_id)
    if not valid_schedule_format(file_name):
        await call.answer(lx.NOT_SCHEDULE_FORMAT, show_alert=True)
        logging.info(f'file {file_name} doesnt pass the schedule test')
        return
    schedule_path = PATH + file_name
    await bot.download_file(
        file_path=file.file_path,
        destination=schedule_path
    )
    df, week_num, schedule_exists = await process_schedule_file(schedule_path)
    if not week_num:
        await call.answer(lx.DIDNT_PARSE, show_alert=True)
        return
    await call.answer()
    if action == 'init':
        if schedule_exists:
            await call.message.edit_text(
                reply_markup=await schedule_exists_kb(callback_data.file_id),
                text=lx.SCHEDULE_EXISTS.format(
                    start=schedule_exists['start'],
                    end=schedule_exists['end'])
            )
        else:
            await call.message.edit_text(lx.FILE_SAVED.format('Расписания'))
            await upload_schedule(df, week_num)
            await call.answer(text=lx.SCHEDULE_UPLOADED, show_alert=True)
            logging.info('schedule uploaded')
    elif action == SchdUpdButt.UPDATE.value:
        db.erase_existing_schedule(week_num)
        await upload_schedule(df, week_num)
        await call.message.edit_text(lx.SCHEDULE_UPDATED)
        logging.info('schedule updated')
    elif action == SchdUpdButt.KEEP.value:
        await call.message.edit_text(lx.KEEP_SCHEDULE)
        logging.info('schedule keep as it was')
    os.remove(schedule_path)


# если пользователь выбрал учебные материалы, даем выбрать предмет
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.STUDY.name))
async def subj_choice(call: CallbackQuery, callback_data: FileCallback):
    await call.answer()
    users_subjects = db.get_users_subjects(call.from_user.id)
    print(users_subjects)
    markup = await subjects_kb(users_subjects, callback_data.file_id)
    await call.message.edit_text(
        text=lx.CHOOSE_SUBJ,
        reply_markup=markup
    )
    logging.debug('you are in study materials section')


# выбор типа материала и сохранение
@dp.callback_query(LibCallback.filter(F.type == 'None'))
async def choose_lib_type(call: CallbackQuery, callback_data: LibCallback):
    await call.answer()
    markup = await lib_type_kb(callback_data.subject_id, callback_data.file_id)
    await call.message.edit_text(
        text=lx.CHOOSE_TYPE,
        reply_markup=markup
    )

# подтверждение выбора
@dp.callback_query(LibCallback.filter(F.confirm == 'None'))
async def choose_lib_type(call: CallbackQuery, callback_data: LibCallback):
    await call.answer()
    markup = await confirm_subj_kb(callback_data.file_id,
                                   callback_data.subject_id,
                                   callback_data.type)
    subj_inv = {v: k for k, v in db.get_users_subjects(call.from_user.id).items()}
    subj_name = subj_inv[callback_data.subject_id]
    subj_type = FileTypeButt._member_map_[callback_data.type].value
    msg = lx.CONFIRM_SUBJECT.format(subj_type.lower(), subj_name)
    await call.message.edit_text(
        text=msg,
        reply_markup=markup
    )

#сохранение если все ок, или откат назад если пользователь нажал отмена
@dp.callback_query(LibCallback.filter(F.confirm != 'None'))
async def confirm_subj(call: CallbackQuery, callback_data: LibCallback):
    await call.answer()
    if callback_data.confirm == Confirm.OK.name:
        file_name, tg_file_id = db.update_file(
            file_id=callback_data.file_id,
            file_type=callback_data.type,
            subj_id=callback_data.subject_id
        )
        subj_inv = {v: k for k, v in db.get_users_subjects(call.from_user.id).items()}
        subj_name = subj_inv[callback_data.subject_id]
        subj_type = FileTypeButt._member_map_[callback_data.type].value
        await call.message.edit_text(
            lx.CONFIRM_SUBJECT_OK.format(subj_type, subj_name)
        )
    else:
        await call.message.edit_text(
            text=lx.FILE_ATTACHED.format(''),
            reply_markup=await file_kb(callback_data.file_id)
        )


# если пользователь выбрал не сохранять
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.CANCEL.name))
async def dont_save_choice(call: CallbackQuery, callback_data: FileCallback):
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer('ok', show_alert=True)
    await bot.delete_message(
        chat_id=chat_id,
        message_id=msg_id)

