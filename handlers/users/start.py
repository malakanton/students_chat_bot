import logging
from lib import lexicon as lx
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from loader import dp, db, gr
from handlers.filters import user_filter, cb_user_filter, UnRegisteredUser
from keyboards.callbacks import StartCallback
from keyboards.start import course_kb, groups_kb
from lib.misc import prep_markdown


@dp.message(CommandStart(),
            user_filter)
async def start(message: Message):
    logging.info(f'groups: {gr.groups}')
    logging.info(f'courses: {gr.courses}')
    logging.debug('start command in private chat')
    user_id = message.from_user.id
    user_group = db.get_user_group(user_id)
    if not user_group:
        hello_msg = lx.HELLO.format(message.from_user.first_name)
        await message.answer(
            text=hello_msg,
            reply_markup=await course_kb(gr.courses),
            parse_mode='MarkdownV2'
        )
    else:
        await message.answer(
            text=lx.YOURE_REGISTERED.format(user_group[1])
        )
        logging.info(f'user {user_id} is already registered')
    await message.delete()


@dp.callback_query(StartCallback.filter(), cb_user_filter)
async def callback_start(call: CallbackQuery, callback_data: StartCallback):
    logging.info('start callback processing in private chat')
    groups = db.get_groups()
    await call.answer()
    if callback_data.group_id == 'None':
        markup = await groups_kb(groups, int(callback_data.course))
        await call.message.edit_text(lx.GROUP_CHOICE, reply_markup=markup)
    else:
        user_id = call.message.chat.id
        user_name = call.message.chat.first_name
        last_name = call.message.chat.last_name
        if last_name:
            user_name += ' ' + last_name
        tg_login = call.message.chat.username
        group_id = callback_data.group_id
        user_group = db.add_user(user_id, group_id, user_name, tg_login)
        logging.info(f'New user added: {user_id} - {user_group[1]}')
        txt = prep_markdown(lx.ADDED_TO_GROUP.format(user_group[1]))
        await call.message.edit_text(text=txt,
                                     parse_mode='MarkdownV2')


# фильтр для незарегистрированных пользователей
@dp.message(user_filter, UnRegisteredUser())
async def unregistered_user(message: Message):
    await message.answer(lx.NOT_REGISTERED, parse_mode='MarkdownV2')
