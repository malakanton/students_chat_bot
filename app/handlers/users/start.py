from aiogram import F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated
from handlers.filters import UnRegisteredUser
from handlers.routers import users_router
from keyboards.buttons import Confirm, Start, StudyFormKb, TeachersButt
from keyboards.callbacks import StartCallback, TeachersCallback
from keyboards.start import confirm_kb, course_kb, groups_kb, role_selector_kb, choose_study_form
from keyboards.teachers import teachers_list_kb, TEACHERS_PER_PAGE, teacher_confirm_kb
from lib.logs import logging_msg
from handlers.states import StartUser
from aiogram.fsm.context import FSMContext
from lib.misc import prep_markdown
from lib.models.group import Groups, StudyForm
from lib.models.users import User, Teacher
from loader import bot, db, lx, schd, users
from lib.config.config import cfg
from loguru import logger
from typing import Tuple


@users_router.my_chat_member()
async def my_chat_member_handler(my_chat_member: ChatMemberUpdated) -> None:
    # TODO: write a scenarios when user deletes the bot
    print("my chat member")
    print(my_chat_member)


# ChatMemberUpdated(chat=Chat(id=401939802, type='private', title=None, username='malakanton', first_name='Anton', last_name='M', is_forum=None, photo=None, active_usernames=None, available_reactions=None, accent_color_id=None, background_custom_emoji_id=None, profile_accent_color_id=None, profile_background_custom_emoji_id=None, emoji_status_custom_emoji_id=None, emoji_status_expiration_date=None, bio=None, has_private_forwards=None, has_restricted_voice_and_video_messages=None, join_to_send_messages=None, join_by_request=None, description=None, invite_link=None, pinned_message=None, permissions=None, slow_mode_delay=None, message_auto_delete_time=None, has_aggressive_anti_spam_enabled=None, has_hidden_members=None, has_protected_content=None, has_visible_history=None, sticker_set_name=None, can_set_sticker_set=None, linked_chat_id=None, location=None), from_user=User(id=401939802, is_bot=False, first_name='Anton', last_name='M', username='malakanton', language_code='en', is_premium=True, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None), date=datetime.datetime(2024, 5, 30, 22, 9, 56, tzinfo=TzInfo(UTC)), old_chat_member=ChatMemberMember(status=<ChatMemberStatus.MEMBER: 'member'>, user=User(id=6510929369, is_bot=True, first_name='ElmoBot', last_name=None, username='KonstantinSergeevichBot', language_code=None, is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None)), new_chat_member=ChatMemberBanned(status=<ChatMemberStatus.KICKED: 'kicked'>, user=User(id=6510929369, is_bot=True, first_name='ElmoBot', last_name=None, username='KonstantinSergeevichBot', language_code=None, is_premium=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None, supports_inline_queries=None), until_date=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=TzInfo(UTC))), invite_link=None, via_chat_folder_invite_link=None)


@users_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    logger.info(logging_msg(message, "start command in private chat"))
    existing_user = db.get_user(message.chat.id)

    if not existing_user:
        hello_msg = prep_markdown(lx.HELLO.format(message.chat.first_name))
        await message.answer(text=hello_msg, reply_markup=await role_selector_kb())

        await state.set_state(StartUser.choose_role)

    else:
        await message.answer(
            text=prep_markdown(lx.YOURE_REGISTERED)
        )
        logger.info(f"user {message.from_user.id} is already registered")

    await message.delete()


@users_router.callback_query(StateFilter(StartUser.choose_role))
async def choose_role(callback: CallbackQuery, state: FSMContext):
    if callback.data == Start.STUDENT.name:
        await callback.message.edit_text(
            text=lx.STUDY_FORM_CHOICE,
            reply_markup=await choose_study_form()
        )
        await state.set_state(StartUser.choose_study_form)

    elif callback.data == Start.TEACHER.name:
        teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.last_name)

        await callback.message.edit_text(
            text=lx.TEACHER_CHOOSEN,
            reply_markup=await teachers_list_kb(teachers, 0),
        )
        await state.set_state(StartUser.choose_teacher)


############### for teachers ###############

@users_router.callback_query(TeachersCallback.filter(F.id < 0))
async def paginate(callback: CallbackQuery, callback_data: TeachersCallback):
    await callback.answer()

    teachers = sorted(schd.get_teachers(), key=lambda teacher: teacher.last_name)
    index = callback_data.index
    if callback_data.paginate == TeachersButt.RIGHT.name:
        if index + TEACHERS_PER_PAGE < len(teachers):
            index += TEACHERS_PER_PAGE

    if callback_data.paginate == TeachersButt.LEFT.name:
        if index - TEACHERS_PER_PAGE >= 0:
            index -= TEACHERS_PER_PAGE

    markup = await teachers_list_kb(teachers, index)

    await callback.message.edit_reply_markup(
        reply_markup=markup
    )


@users_router.callback_query(StateFilter(StartUser.teacher_confirm))
async def teacher_choosen(callback: CallbackQuery, state: FSMContext):
    callback_data = TeachersCallback.unpack(callback.data)

    await callback.answer()
    if callback_data.confirm == Confirm.CANCEL.name:
        await start(callback.message, state)
        return

    resp = schd.register_teacher(callback_data.id, callback.message.chat.id)

    if isinstance(resp, Teacher):
        await register_teacher_user(callback.message, state, resp)
    else:
        await callback.message.edit_text(
            text=prep_markdown(lx.TEACHER_EXIST),
            reply_markup=None
        )


@users_router.callback_query(TeachersCallback.filter(F.id > 0))
async def confirm_teacher(callback: CallbackQuery, state: FSMContext):
    teacher_id = TeachersCallback.unpack(callback.data).id

    markup = await teacher_confirm_kb(teacher_id)
    teacher = schd.get_teachers(teacher_id)

    await callback.message.edit_text(
        text=prep_markdown(lx.TEACHER_CONFIRM.format(teacher.last_name + ' ' + teacher.initials)),
        reply_markup=markup
    )
    await state.set_state(StartUser.teacher_confirm)


async def register_teacher_user(message: Message, state: FSMContext, teacher: Teacher) -> None:
    tg_name, login = get_name_login(message)
    name = tg_name
    if teacher.first_name and teacher.fathers_name:
        name = teacher.first_name + ' ' + teacher.fathers_name

    text = lx.TEACHER_REGISTERED.format(name) + '\n\n' + lx.DESCRIPTION_FOR_TEACHERS
    u = User(
        id=message.chat.id,
        name=name,
        tg_login=login,
        role='teacher',
        teacher_id=teacher.id,
    )
    db.add_user(u)

    await bot.send_message(
        cfg.secrets.ADMIN_CHAT,
        text=f"New teacher user added: @{login} {tg_name} {message.chat.id} - teacher: {teacher.last_name} {teacher.initials} ",
        parse_mode="HTML",
    )

    users.update(db)
    await message.delete()
    await message.answer(prep_markdown(text))

    await state.clear()

############### for students ###############


@users_router.callback_query(StateFilter(StartUser.choose_study_form))
async def chose_study_form(callback: CallbackQuery, state: FSMContext):
    form = StudyForm.INT
    groups = schd.get_groups()
    if not isinstance(groups, Groups):
        logger.error(f'failed to get groups list from schedule service: {groups}')
        return

    if callback.data == StudyFormKb.EXTRAMURAL.name:
        form = StudyForm.EXT

    groups.filter_study_type(form.value)

    markup = await course_kb(groups.courses, form)
    await callback.message.edit_text(
        text=lx.COURSE_CHOICE,
        reply_markup=markup
    )
    await state.set_state(StartUser.choose_course)


@users_router.callback_query(StateFilter(StartUser.choose_course))
async def choose_group(callback: CallbackQuery, state: FSMContext):
    callback_data = StartCallback.unpack(callback.data)
    course = callback_data.course
    form = callback_data.form

    groups = schd.get_groups()
    groups.filter_study_type(form)

    markup = await groups_kb(groups, course, form)
    await callback.message.edit_text(
        text=lx.GROUP_CHOICE,
        reply_markup=markup
    )
    await state.set_state(StartUser.choose_group)


@users_router.callback_query(StateFilter(StartUser.choose_group))
async def confirm_group(callback: CallbackQuery, state: FSMContext):
    callback_data = StartCallback.unpack(callback.data)
    group_id = callback_data.group_id
    group_name = callback_data.group_name

    markup = await confirm_kb(group_id, group_name)
    await callback.message.edit_text(
        text=prep_markdown(lx.GROUP_CONFIRM.format(group_name)),
        reply_markup=markup
    )
    await state.set_state(StartUser.confirm)


@users_router.callback_query(StateFilter(StartUser.confirm))
async def confirmed(callback: CallbackQuery, state: FSMContext):
    callback_data = StartCallback.unpack(callback.data)
    group_id = callback_data.group_id
    group_name = callback_data.group_name
    confirm = callback_data.confirm
    await state.clear()

    if confirm == Confirm.OK.name:
        role = get_role(group_id)

        name, login = get_name_login(callback.message)
        u = User(
            id=callback.message.chat.id,
            name=name,
            tg_login=login,
            role=role,
            group_id=group_id,
        )

        db.add_user(u)
        users.update(db)
        logger.info(f"New user added: {callback.message.chat.id} - {group_name}")
        await callback.message.edit_text(
            text=prep_markdown(lx.ADDED_TO_GROUP.format(u.name, group_name))
        )

        await bot.send_message(
            cfg.secrets.ADMIN_CHAT,
            text=f"New user added: @{login} {name} {callback.message.chat.id} - group: {group_name}",
            parse_mode="HTML",
        )

    else:
        await start(callback.message, state)


# фильтр для незарегистрированных пользователей
@users_router.message(UnRegisteredUser())
async def unregistered_user(message: Message):
    logger.info(logging_msg(message, "unregistered user"))
    await message.answer(prep_markdown(lx.NOT_REGISTERED))


def get_role(group_id: int) -> str:
    groups = schd.get_groups()
    group = groups.get_group_by_id(group_id)
    if group.study_form == 1:
        return 'intramural'

    return 'unreg'


def get_name_login(message: Message) -> Tuple[str, str]:

    name = message.chat.first_name

    if message.chat.last_name:
        name += ' ' + message.chat.last_name
    login = message.chat.username

    return name, login
