import logging
from lib import lexicon as lx
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from loader import dp, bot, db, gr
from lib.models import Groups
from handlers.filters import GroupFilter, IsRegisteredGroup, cb_group_filter
from keyboards.callbacks import StartCallback
from keyboards.buttons import Confirm
from keyboards.start import course_kb, groups_kb, confirm_kb
from lib.misc import chat_msg_ids, prep_markdown
import asyncio
from config import UNAUTHORIZED_GROUP_TIMOUT, ADMIN_CHAT


@dp.message(CommandStart(), GroupFilter)
async def start(message: Message):
    logging.debug('start command in group chat!')
    markup = await course_kb(gr.courses)
    hello_msg = lx.COURSE_CHOICE
    chat_id = message.chat.id
    gr_list = Groups(db.get_groups())
    for group in gr_list.groups:
        if chat_id == group.chat_id:
            await message.answer(
                prep_markdown(lx.CHAT_IS_LINKED.format(group.name))
            )
            logging.info(f'chat {chat_id} is already registered')
            await message.delete()
            return
    await message.answer(
        text=hello_msg,
        reply_markup=markup
    )


@dp.callback_query(StartCallback.filter(),
                   cb_group_filter,
                   StartCallback.filter(F.confirm == 'None'))
async def group_choice(call: CallbackQuery, callback_data: StartCallback):
    logging.info('start callback processing in private chat')
    gr_list = Groups(db.get_groups())
    await call.answer()
    if callback_data.group_id == 'None':
        markup = await groups_kb(gr_list.groups, int(callback_data.course))
        await call.message.edit_text(prep_markdown(lx.GROUP_CHOICE), reply_markup=markup)
    else:
        group = gr_list.groups[int(callback_data.group_id)-1]
        markup = await confirm_kb(group.course, group)
        msg = prep_markdown(lx.GROUP_CONFIRM.format(group.name))
        await call.message.edit_text(msg,
                                     reply_markup=markup)


@dp.callback_query(StartCallback.filter(), cb_group_filter)
async def confirm(call: CallbackQuery, callback_data: StartCallback):
    gr_list = Groups(db.get_groups())
    groups = gr_list.groups
    chat_id, msg_id = chat_msg_ids(call)
    if callback_data.confirm == Confirm.OK.name:
        group_id = int(callback_data.group_id)
        if await unauthorized_chat(call, groups, group_id):
            await call.answer(lx.GROUP_CHAT_VIOLATION, show_alert=True)
            await bot.leave_chat(chat_id)
            return
        group_name = db.update_group_chat(group_id, chat_id)
        #TODO add users update status
        logging.info(f'New group chat added: {chat_id} - {group_name}')
        global gr
        gr = Groups(db.get_groups())
        await call.message.edit_text(prep_markdown(lx.GROUP_LINKED.format(group_name)))
    else:
        await call.message.edit_text(
            text=lx.COURSE_CHOICE,
            reply_markup=await course_kb(gr_list.courses)
        )


@dp.message(GroupFilter,
            F.text,
            ~F.text.startswith('/start'),
            ~IsRegisteredGroup(gr.chats|set(ADMIN_CHAT))
async def leave_if_unauthorised(message: Message):
    await asyncio.sleep(UNAUTHORIZED_GROUP_TIMOUT)
    if message.chat.id not in gr.chats:
        logging.warning('unauthorized group!!!')
        await bot.leave_chat(message.chat.id)


async def unauthorized_chat(call, groups, chosen_group_id) -> bool:
    print('choosen group id: ', chosen_group_id)
    for group in groups:
        if (
                group.id == chosen_group_id and
                group.chat_id
        ):
            logging.warning(
                f'trying to attach a bot to a wrong chat: {call.message.chat.id}. The group {group.name} have a chat ({group.chat_id}) already')
            await call.answer(lx.GROUP_CHAT_VIOLATION, show_alert=True)
            return True
