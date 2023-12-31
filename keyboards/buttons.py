from enum import Enum


COURSES = {
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣'
}


class FileButt(Enum):
    CANCEL = 'Не сохраняй'
    STUDY = 'Полезный стафф'
    SCHEDULE = 'Расписание'


class SchdUpdButt(Enum):
    UPDATE = 'Обнови'
    KEEP = 'Не обновляй'


class CancelButt(Enum):
    CANCEL = 'Отмена'
    BACK = 'Назад'


class ScheduleButt(Enum):
    BACK = '⬅️'
    WEEK = 'Вся неделя'
    FORW = '➡️'


codes = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
