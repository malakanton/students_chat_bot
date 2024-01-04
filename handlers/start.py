from aiogram import types
from aiogram.dispatcher.filters import Command
import bot_replies as br
from loader import dp, bot, db
from keyboards.keyboards import start_kb, start_cb
import datetime as dt
from lib.misc import chat_msg_ids


@dp.message_handler(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_group = db.get_user_group(user_id)
    if not user_group:
        hello_msg = f'Привет, <b>{message.from_user.first_name}</b>!\n'
        hello_msg += br.DESCRIPTION
        groups = db.get_groups()
        await bot.send_sticker(message.chat.id, sticker=br.HELLO_STICKER)
        await message.answer(
            text=hello_msg,
            parse_mode='html',
            reply_markup=start_kb(groups)
        )
    else:
        msg = f'Ты уже записан в группу {user_group[1]}'
        await message.answer(
            text=msg,
            parse_mode='html'
        )
    await message.delete()


@dp.callback_query_handler(start_cb.filter())
async def callback_start(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    chat_id, msg_id = chat_msg_ids(call)
    user_id = call.message.chat.id
    user_name = call.message.chat.first_name
    last_name = call.message.chat.last_name
    if last_name:
        user_name += ' ' + last_name
    tg_login = call.message.chat.username
    group_id = callback_data['group_id']
    date = dt.datetime.now()
    user_group = db.add_user(user_id, group_id, user_name, tg_login, date)
    print(f'New user added: {user_id} - {user_group[1]}')
    msg = f'Добавил тебя в группу {user_group[1]}'
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=msg
    )
