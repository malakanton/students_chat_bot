import asyncio

from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from handlers.filters import IsRegisteredGroup
from handlers.routers import groups_router
from keyboards.buttons import Confirm
from keyboards.callbacks import StartCallback
from keyboards.start import confirm_kb, course_kb, groups_kb
from lib.misc import chat_msg_ids, prep_markdown
from lib.models.group import Groups
from loader import bot, db, lx
from lib.config.config import cfg
from loguru import logger


@groups_router.message(CommandStart())
async def start(message: Message):
    logger.debug("start command in group chat!")
    markup = await course_kb(gr.courses)
    hello_msg = lx.COURSE_CHOICE
    chat_id = message.chat.id
    gr_list = Groups(db.get_groups())
    for group in gr_list.groups:
        if chat_id == group.chat_id:
            await message.answer(prep_markdown(lx.CHAT_IS_LINKED.format(group.name)))
            logger.info(f"chat {chat_id} is already registered")
            await message.delete()
            return
    await message.answer(text=hello_msg, reply_markup=markup)


@groups_router.callback_query(
    StartCallback.filter(), StartCallback.filter(F.confirm == "None")
)
async def group_choice(call: CallbackQuery, callback_data: StartCallback):
    logger.info("start callback processing in private chat")
    gr_list = Groups(db.get_groups())
    await call.answer()
    if callback_data.group_id == "None":
        markup = await groups_kb(gr_list.groups, int(callback_data.course))
        await call.message.edit_text(
            prep_markdown(lx.GROUP_CHOICE), reply_markup=markup
        )
    else:
        group = gr_list.groups[int(callback_data.group_id) - 1]
        markup = await confirm_kb(group.course, group)
        msg = prep_markdown(lx.GROUP_CONFIRM.format(group.name))
        await call.message.edit_text(msg, reply_markup=markup)


@groups_router.callback_query(StartCallback.filter())
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
        logger.info(f"New group chat added: {chat_id} - {group_name}")
        global gr
        gr = Groups(db.get_groups())
        await call.message.edit_text(prep_markdown(lx.GROUP_LINKED.format(group_name)))
    else:
        await call.message.edit_text(
            text=lx.COURSE_CHOICE, reply_markup=await course_kb(gr_list.courses)
        )


@groups_router.message(
    F.text, ~F.text.startswith("/start"), ~IsRegisteredGroup(gr.chats)
)
async def leave_if_unauthorised(message: Message):
    await asyncio.sleep(cfg.UNAUTHORIZED_GROUP_TIMOUT)
    if message.chat.id not in gr.chats:
        logger.warning("unauthorized group!!!")
        await bot.leave_chat(message.chat.id)


async def unauthorized_chat(call, groups, chosen_group_id) -> bool:
    print("choosen group id: ", chosen_group_id)
    for group in groups:
        if group.id == chosen_group_id and group.chat_id:
            logger.warning(
                f"trying to attach a bot to a wrong chat: {call.message.chat.id}. The group {group.name} have a chat ({group.chat_id}) already"
            )
            await call.answer(lx.GROUP_CHAT_VIOLATION, show_alert=True)
            return True
