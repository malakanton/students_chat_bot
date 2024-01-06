import logging
from aiogram.types import Message, CallbackQuery
from loader import dp, bot, db
from aiogram.filters import Command, CommandStart
import bot_replies as br
from keyboards.callbacks import StartCallback
from keyboards.keyboards import course_kb, groups_kb
from lib.misc import chat_msg_ids


@dp.message(CommandStart())
async def start(message: Message):
    logging.debug('start command!')
    chat_type = message.chat.type
    courses = [1, 2, 3]
    markup = await course_kb(courses)
    hello_msg = br.DESCRIPTION
    if chat_type == 'private':
        user_id = message.from_user.id
        user_group = db.get_user_group(user_id)
        if not user_group:
            hello_msg = f'Привет, <b>{message.from_user.first_name}</b>!\n' + hello_msg
            await message.answer(
                text=hello_msg,
                reply_markup=markup
            )
        else:
            await message.answer(
                text=f'Ты уже записан в группу {user_group[1]}'
            )
            logging.info(f'user {user_id} is already registered')
    elif chat_type == 'group':
        chat_id = message.chat.id
        groups = db.get_groups()
        for group in groups:
            if chat_id == group.chat_id:
                await message.answer(
                    text=f'Чат закреплен за группой {group.name}'
                )
                logging.info(f'chat {chat_id} is already registered')
                return
        await message.answer(
            text=hello_msg,
            reply_markup=markup
        )
    await message.delete()


@dp.callback_query(StartCallback.filter())
async def callback_start(call: CallbackQuery, callback_data: StartCallback):
    groups = db.get_groups()
    chat_id, msg_id = chat_msg_ids(call)
    chat_type = call.message.chat.type
    if callback_data.group_id == 'None':
        markup = await groups_kb(groups, int(callback_data.course))
        await call.message.edit_text('Выбери группу', reply_markup=markup)
    else:
        await call.answer()
        if chat_type == 'private':
            user_id = call.message.chat.id
            user_name = call.message.chat.first_name
            last_name = call.message.chat.last_name
            if last_name:
                user_name += ' ' + last_name
            tg_login = call.message.chat.username
            group_id = callback_data.group_id
            user_group = db.add_user(user_id, group_id, user_name, tg_login)
            logging.info(f'New user added: {user_id} - {user_group[1]}')
            msg = f'Добавил тебя в группу {user_group[1]}'
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=msg
            )
        elif chat_type == 'group':
            group_id = callback_data.group_id
            group_name = db.update_group_chat(group_id, chat_id)
            logging.info(f'New group chat added: {chat_id} - {group_name}')
            msg = f'Закрепил чат за группой {group_name}'
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=msg
            )
