from aiogram import types
from aiogram.dispatcher.filters import Command
import bot_replies as br
from loader import dp, bot, db
from keyboards.keyboards import course_kb, start_cb, groups_kb
import datetime as dt
from lib.misc import chat_msg_ids


@dp.message_handler(Command('start'))
async def start(message: types.Message):
    chat_type = message.chat.type
    courses = [1, 2, 3]
    markup = course_kb(courses)
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
    elif chat_type == 'group':
        chat_id = message.chat.id
        groups = db.get_groups()
        for group in groups:
            if chat_id == group.get('chat_id', ''):
                await message.answer(
                    text=f'Чат закреплен за группой {group["name"]}'
                )
                return
        await message.answer(
            text=hello_msg,
            reply_markup=markup
        )
    await message.delete()


@dp.callback_query_handler(start_cb.filter())
async def callback_start(call: types.CallbackQuery, callback_data: dict):
    groups = db.get_groups()
    chat_type = call.message.chat.type
    if callback_data['group_id'] == 'None':
        markup = groups_kb(groups, int(callback_data['course']))
        await call.message.edit_text('Выбери группу', reply_markup=markup)
    else:
        chat_id, msg_id = chat_msg_ids(call)
        await call.answer()
        if chat_type == 'private':
            user_id = call.message.chat.id
            user_name = call.message.chat.first_name
            last_name = call.message.chat.last_name
            if last_name:
                user_name += ' ' + last_name
            tg_login = call.message.chat.username
            group_id = callback_data['group_id']
            user_group = db.add_user(user_id, group_id, user_name, tg_login)
            print(f'New user added: {user_id} - {user_group[1]}')
            msg = f'Добавил тебя в группу {user_group[1]}'
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=msg
            )
        elif chat_type == 'group':
            group_id = callback_data['group_id']
            chat_id = call.message.chat.id
            group_name = db.update_group_chat(group_id, chat_id)
            print(f'New group chat added: {chat_id} - {group_name}')
            msg = f'Закрепил чат за группой {group_name}'
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=msg
            )
