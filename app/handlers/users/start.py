import logging
from aiogram import F
from lib import lexicon as lx
from lib.models import Groups
from lib.misc import prep_markdown
from loader import dp, db, gr, users
from keyboards.buttons import Confirm
from aiogram.filters import CommandStart
from keyboards.callbacks import StartCallback
from aiogram.types import Message, CallbackQuery
from keyboards.start import course_kb, groups_kb, confirm_kb
from handlers.filters import UserFilter, cb_user_filter, UnRegisteredUser


@dp.message(CommandStart(),
            UserFilter())
async def start(message: Message):
    logging.info(f'groups: {gr.groups}')
    logging.info(f'courses: {gr.courses}')
    logging.debug('start command in private chat')
    user_id = message.from_user.id
    user_group = db.get_user_group(user_id)
    if not user_group:
        hello_msg = prep_markdown(lx.HELLO.format(message.from_user.first_name) + lx.COURSE_CHOICE)
        await message.answer(
            text=hello_msg,
            reply_markup=await course_kb(gr.courses)
        )
    else:
        await message.answer(
            text=prep_markdown(lx.YOURE_REGISTERED.format(user_group[1]))
        )
        logging.info(f'user {user_id} is already registered')
    await message.delete()


@dp.callback_query(StartCallback.filter(F.confirm == 'None'),
                   cb_user_filter)
async def callback_start(call: CallbackQuery, callback_data: StartCallback):
    logging.info('start callback processing in private chat')
    groups = db.get_groups()
    await call.answer()
    if callback_data.group_id == 'None':
        markup = await groups_kb(groups, int(callback_data.course))
        await call.message.edit_text(lx.GROUP_CHOICE, reply_markup=markup)
    else:
        group = gr.groups[int(callback_data.group_id)-1]
        markup = await confirm_kb(group.course, group)
        msg = prep_markdown(lx.GROUP_CONFIRM.format(group.name))
        await call.message.edit_text(msg,
                                     reply_markup=markup)


@dp.callback_query(StartCallback.filter(F.confirm != 'None'),
                   cb_user_filter)
async def confirm(call: CallbackQuery, callback_data: StartCallback):
    await call.answer()
    gr = Groups(db.get_groups())
    if callback_data.confirm == Confirm.OK.name:
        user_id = call.message.chat.id
        user_name = call.message.chat.first_name
        last_name = call.message.chat.last_name
        if last_name:
            user_name += ' ' + last_name
        tg_login = call.message.chat.username
        group_id = callback_data.group_id
        if gr.groups[int(group_id)-1].chat_id:
            user_group = db.add_user(user_id, group_id, user_name, tg_login, 'regular')
            users.regular.add(user_id)
        else:
            user_group = db.add_user(user_id, group_id, user_name, tg_login)
            users.unreg.add(user_id)
        logging.info(f'New user added: {user_id} - {user_group[1]}')
        txt = prep_markdown(lx.ADDED_TO_GROUP.format(user_name, user_group[1]) +
                            lx.DESCRIPTION)
        await call.message.edit_text(text=txt)
        print(users)
    else:
        await call.message.edit_text(
            text=lx.COURSE_CHOICE,
            reply_markup=await course_kb(gr.courses)
        )


# фильтр для незарегистрированных пользователей
@dp.message(UserFilter(), UnRegisteredUser())
async def unregistered_user(message: Message):
    await message.answer(
        prep_markdown(lx.NOT_REGISTERED)
    )
