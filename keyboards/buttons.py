from enum import Enum


COURSES = {
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣'
}


class Confirm(Enum):
    OK = '✅Да!'
    CANCEL = '❌Заново'


class FileButt(Enum):
    CANCEL = 'Не сохраняй'
    STUDY = 'Полезный стафф'
    SCHEDULE = 'Расписание'


class SchdUpdButt(Enum):
    UPDATE = 'Обнови'
    KEEP = 'Не обновляй'


class FileTypeButt(Enum):
    LECTURE = 'Лекцию'
    BLANK = 'Шаблон'
    TASK = 'Задание'
    HOMEWORK = 'Домашку'
    ADDITIONAL = 'Доп материалы'


class CancelButt(Enum):
    CANCEL = 'Отмена'
    BACK = 'Назад'


class ScheduleButt(Enum):
    BACK = '⬅️'
    WEEK = 'Вся неделя'
    FORW = '➡️'


codes = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']


