from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix='start'):
    course: int
    group_id: str
    confirm: str


class FileCallback(CallbackData, prefix='file'):
    file_type: str
    file_id: int
    update: str


class ScheduleCallback(CallbackData, prefix='schedule'):
    week: int
    command: str


class LibCallback(CallbackData, prefix='lib'):
    file_id: int
    subject_id: int
    type: str
    confirm: str


class LessonLinkCallback(CallbackData, prefix='link'):
    msg_id: int
    date: str
    time: str
    subj_id: int


class Notifications(CallbackData, prefix='notif'):
    flag: str
