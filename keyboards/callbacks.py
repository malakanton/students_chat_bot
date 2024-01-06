from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix='start'):
    course: int
    group_id: str


class FileCallback(CallbackData, prefix='file'):
    file_type: str
    file_id: int
    update: str


class ScheduleCallback(CallbackData, prefix='schedule'):
    week: int
    day: int