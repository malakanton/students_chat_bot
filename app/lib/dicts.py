from enum import Enum


class NotificationsAdvance(Enum):
    FIVE = 5
    TEN = 10
    FIFTEEN = 15
    THIRTY = 30


RU_DAYS = {
    'Понедельник': 1,
    'Вторник': 2,
    'Среда': 3,
    'Четверг': 4,
    'Пятница': 5,
    'Суббота': 6
}
LESSONS_DICT = {
        1: 'Одна пара:',
        2: 'Две пары:',
        3: 'Три пары:',
        4: 'Четыре пары:',
        5: 'Пять пар:',
        6: 'Шесть пар:'
    }

MONTHS = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',

}
RU_DAYS_INV = {v: k for k, v in RU_DAYS.items()}

PERMANENT_LINKS = {
    3: 'https://t.me/c/1917581433/75', # Ильин
    4: 'https://t.me/+cMt0bqkaiIVkNmEy', # Ерболова
    22: 'https://t.me/PROG_mod', # Кузин
    57: 'https://t.me/+jYLYdPiB5xUyNzgy' # менеджмент
}
