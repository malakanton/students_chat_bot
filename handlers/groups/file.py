import os
import logging
from aiogram.types import Message, CallbackQuery
from config import PATH
from aiogram import F
from lib import lexicon as lx
from loader import dp, db, bot
from handlers.filters import group_filter
from keyboards.file import schedule_exists_kb, file_kb
from keyboards.callbacks import FileCallback
from lib.misc import chat_msg_ids, valid_schedule_format
from lib.schedule_uploader import process_schedule_file, upload_schedule
from keyboards.buttons import FileButt, SchdUpdButt


# обработка прикрепленных документов
@dp.message(F.content_type == 'document',
            group_filter)
async def document_processing(message: Message):
    logging.info(f'document uploaded in group {message.chat.id}')
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
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.SCHEDULE.name),
                   group_filter)
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
    if action == 'init':
        if schedule_exists:
            await call.answer()
            await call.message.edit_text(
                reply_markup=await schedule_exists_kb(callback_data.file_id),
                text=lx.SCHEDULE_EXISTS.format(
                    start=schedule_exists['start'],
                    end=schedule_exists['end'])
            )
        else:
            await call.message.edit_text(lx.FILE_SAVED.format('Расписания'))
            not_uploaded = await upload_schedule(df, week_num)
            if not_uploaded:
                logging.warning(f'didnt manage to find groups {not_uploaded}')
            await call.answer(text=lx.SCHEDULE_UPLOADED, show_alert=True)
            logging.info('schedule uploaded')
    elif action == SchdUpdButt.UPDATE.value:
        await call.answer()
        db.erase_existing_schedule(week_num)
        not_uploaded = await upload_schedule(df, week_num)
        if not_uploaded:
            logging.warning(f'didnt manage to find groups {not_uploaded}')
        await call.message.edit_text(lx.SCHEDULE_UPDATED)
        logging.info('schedule updated')
    elif action == SchdUpdButt.KEEP.value:
        await call.answer()
        await call.message.edit_text(lx.KEEP_SCHEDULE)
        logging.info('schedule keep as it was')
    os.remove(schedule_path)


# если пользователь выбрал учебные материалы
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.STUDY.name))
async def study_file_choice(call: CallbackQuery, callback_data: FileCallback):
    # здесь надо добавить клавиатуру с выбором предмета
    # список надо делать для группы пользователя из базы
    #
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer('not able to process study materials yet..', show_alert=True)
    file_name, tg_file_id = db.update_file(
        file_id=callback_data.file_id,
        file_type=callback_data.file_type
    )
    file = await bot.get_file(tg_file_id)
    full_path = PATH + file_name
    await bot.download_file(
        file_path=file.file_path,
        destination=full_path
    )
    logging.debug('you are in study materials section')


# если пользователь выбрал не сохранять
@dp.callback_query(FileCallback.filter(F.file_type == FileButt.CANCEL.name))
async def dont_save_choice(call: CallbackQuery, callback_data: FileCallback):
    chat_id, msg_id = chat_msg_ids(call)
    await call.answer('ok', show_alert=True)
    await bot.delete_message(
        chat_id=chat_id,
        message_id=msg_id)
