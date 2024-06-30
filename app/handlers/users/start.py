from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated
from handlers.filters import UnRegisteredUser
from handlers.routers import users_router
from keyboards.buttons import Confirm
from keyboards.callbacks import StartCallback
from keyboards.start import confirm_kb, course_kb, groups_kb
from lib.logs import logging_msg
from lib.misc import prep_markdown
from lib.models import Groups
from loader import bot, db, gr, users, lx
from lib.config.config import cfg
from loguru import logger


@users_router.my_chat_member()
async def my_chat_member_handler(my_chat_member: ChatMemberUpdated) -> None:
    # TODO: write a scenarios when user deletes the bot
    print("my chat member")
    print(my_chat_member)


# ChatMemberUpdated(chat=Chat(id=401939802, type='private', title=None, username='malakanton', first_name='Anton', last_name='M', is_forum=None, photo=None, active_usernames=None, available_reactions=None, accent_color_id=None, background_custom_emoji_id=None, profile_accent_color_id=None, profile_background_custom_emoji_id=None, emoji_status_custom_emoji_id=None, emoji_status_expiration_date=None, bio=None, has_private_forwards=None, has_restricted_voice_and_video_messages=None, join_to_send_messages=None, join_by_request=None, description=None, invite_link=None, pinned_message=None, permissions=None, slow_mode_delay=None, message_auto_delete_time=None, has_aggressive_anti_spam_enabled=None, has_hidden_members=None, has_protected_content=None, has_visible_history=None, sticker_set_name=None, can_set_sticker_set=None, linked_chat_id=None, location=None), from_user=User(id=401939802, is_bot=False, first_name='Anton', last_name='M', username='malakanton', language_code='en', is_premium=True, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None), date=datetime.datetime(2024, 5, 30, 22, 9, 56, tzinfo=TzInfo(UTC)), old_chat_member=ChatMemberMember(status=<ChatMemberStatus.MEMBER: 'member'>, user=User(id=6510929369, is_bot=True, first_name='ElmoBot', last_name=None, username='KonstantinSergeevichBot', language_code=None, is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None)), new_chat_member=ChatMemberBanned(status=<ChatMemberStatus.KICKED: 'kicked'>, user=User(id=6510929369, is_bot=True, first_name='ElmoBot', last_name=None, username='KonstantinSergeevichBot', language_code=None, is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None), until_date=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=TzInfo(UTC))), invite_link=None, via_chat_folder_invite_link=None)


@users_router.message(CommandStart())
async def start(message: Message):
    logger.info(logging_msg(message, "start command in private chat"))
    user_id = message.from_user.id
    name = message.from_user.first_name
    user_group = db.get_user_group(user_id)
    if not user_group:
        hello_msg = prep_markdown(lx.HELLO.format(name) + lx.COURSE_CHOICE)
        await message.answer(text=hello_msg, reply_markup=await course_kb(gr.courses))
    else:
        await message.answer(
            text=prep_markdown(lx.YOURE_REGISTERED.format(user_group[1]))
        )
        logger.info(f"user {user_id} is already registered")
    await message.delete()


# фильтр для незарегистрированных пользователей
@users_router.message(UnRegisteredUser())
async def unregistered_user(message: Message):
    logger.info(logging_msg(message, "unregistered user"))
    await message.answer(prep_markdown(lx.NOT_REGISTERED))


@users_router.callback_query(StartCallback.filter(F.confirm == "None"))
async def callback_start(call: CallbackQuery, callback_data: StartCallback):
    logger.info(logging_msg(call, "start callbacks processing"))
    groups = db.get_groups()
    await call.answer()
    if callback_data.group_id == "None":
        markup = await groups_kb(groups, int(callback_data.course))
        await call.message.edit_text(lx.GROUP_CHOICE, reply_markup=markup)
    else:
        group = gr.groups[int(callback_data.group_id) - 1]
        markup = await confirm_kb(group.course, group)
        msg = prep_markdown(lx.GROUP_CONFIRM.format(group.name))
        await call.message.edit_text(msg, reply_markup=markup)


@users_router.callback_query(StartCallback.filter(F.confirm != "None"))
async def confirm(call: CallbackQuery, callback_data: StartCallback):
    await call.answer()
    logger.info(logging_msg(call, "start callbacks processing"))
    gr = Groups(db.get_groups())

    if callback_data.confirm == Confirm.OK.name:
        user_id, user_name, tg_login = get_user_details(call)
        group_id = callback_data.group_id
        if gr.groups[int(group_id) - 1].chat_id:
            user_type = "regular"
            users.regular.add(user_id)
        else:
            user_type = None
            users.unreg.add(user_id)
        user_group = db.add_user(user_id, group_id, user_name, tg_login, user_type)
        logger.info(f"New user added: {user_id} - {user_group[1]}")
        await bot.send_message(
            cfg.secrets.ADMIN_CHAT,
            text=f"New user added: @{tg_login} {user_name} {user_id} - group: {user_group[1]}",
            parse_mode="HTML",
        )
        gc_link = db.get_user_group(user_id)[2]
        if not gc_link:
            gc_link = "https://calendar.google.com/"
        txt = prep_markdown(
            lx.ADDED_TO_GROUP.format(user_name, user_group[1])
            + lx.DESCRIPTION.format(gc_link)
        )
        await call.message.edit_text(text=txt)

    else:
        await call.message.edit_text(
            text=lx.COURSE_CHOICE, reply_markup=await course_kb(gr.courses)
        )


def get_user_details(call: CallbackQuery) -> tuple:
    user_id = call.message.chat.id
    user_name = call.message.chat.first_name
    last_name = call.message.chat.last_name
    if last_name:
        user_name += " " + last_name
    tg_login = call.message.chat.username
    return user_id, user_name, tg_login
