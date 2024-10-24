from aiogram.filters.callback_data import CallbackData
from typing import Optional


class StartCallback(CallbackData, prefix="start"):
    course: Optional[int]
    form: Optional[int]
    confirm: Optional[str]
    group_id: Optional[int]
    group_name: Optional[str]


class FileCallback(CallbackData, prefix="file"):
    file_type: str
    file_id: int
    update: str


class ScheduleCallback(CallbackData, prefix="schedule"):
    week: int
    command: str


class LibCallback(CallbackData, prefix="lib"):
    file_id: int
    subject_id: int
    type: str
    confirm: str


class LessonLinkCallback(CallbackData, prefix="link"):
    msg_id: int
    date: str
    time: str
    subj_id: int


class NotificationMenu(CallbackData, prefix="notif_menu"):
    action: str
    flag: str
    push_time: str


class ConfirmCallback(CallbackData, prefix="confirm"):
    cnf: str


class TeachersCallback(CallbackData, prefix="teacher"):
    id: int
    paginate: Optional[str]
    index: int
    confirm: Optional[str]
