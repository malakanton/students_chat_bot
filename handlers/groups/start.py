import logging
from lib import lexicon as lx
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from loader import dp, bot, db, gr
from lib.models import Groups
from handlers.filters import group_filter, IsRegisteredGroup, cb_group_filter
from keyboards.callbacks import StartCallback
from keyboards.start import course_kb, groups_kb
from lib.misc import chat_msg_ids


@dp.message(CommandStart(), group_filter)
async def start(message: Message):
    logging.debug('start command in group chat!')
    markup = await course_kb(gr.courses)
    hello_msg = lx.HELLO
    chat_id = message.chat.id
    for group in gr.groups:
        if chat_id == group.chat_id:
            await message.answer(
                lx.CHAT_IS_LINKED.format(group.name)
            )
            logging.info(f'chat {chat_id} is already registered')
            return
    await message.answer(
        text=hello_msg,
        reply_markup=markup
    )
    await message.delete()


@dp.callback_query(StartCallback.filter(), cb_group_filter)
async def callback_start(call: CallbackQuery, callback_data: StartCallback):
    global gr
    groups = gr.groups
    chat_id, msg_id = chat_msg_ids(call)
    if callback_data.group_id == 'None':
        markup = await groups_kb(groups, int(callback_data.course))
        await call.message.edit_text(lx.GROUP_CHOICE, reply_markup=markup)
    else:
        group_id = int(callback_data.group_id)
        if await unauthorized_chat(call, groups, group_id):
            await bot.leave_chat(chat_id)
            return
        group_name = db.update_group_chat(group_id, chat_id)
        logging.info(f'New group chat added: {chat_id} - {group_name}')
        gr = Groups(db.get_groups())
        await call.message.edit_text(lx.GROUP_LINKED.format(group_name))


@dp.message(group_filter,
            ~F.text.startswith('/start'),
            ~IsRegisteredGroup(gr.chats))
async def leave_if_unauthorised(message: Message):
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
