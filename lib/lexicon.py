

HELP_MSG = """
__Команды бота__

📅*/schedule* - посмотреть расписание
📗*/library* - учебные материалы
📋*/description* - про бота
📨*/contacts* - контакты
"""


DESCRIPTION = """
Это бот КТ МТУСИ для очно-заочного отделения.

блаблабла
"""

CONTACTS = """
контакты ОС
"""

MAIN_MENU = {
    '/help': '❔ помощь',
    '/schedule': '📅 посмотреть расписание',
    '/library': '📚 учебные материалы'
}


####################### РЕГИСТРАЦИЯ #######################

HELLO = """
Привет, *{}*\!

Я бот 
"""


COURSE_CHOICE = """На каком ты курсе?"""

GROUP_CHOICE = """А группа какая?"""

YOURE_REGISTERED = """Ты уже в группе {}"""

GROUP_CONFIRM = """Выбрана группа *{}* \nПодтвердить?"""

ADDED_TO_GROUP = """Отлично, добавил тебя в группу *{}*.
Теперь когда попросишь показать расписание, я буду показывать расписание для твоей группы.
Если хочешь посмотреть расписание других групп, то нам с тобой не по пути. 
"""

NOT_REGISTERED = """Эй, сначала надо зарегистрироваться\! для этого жмакни на /start"""

GROUP_LINKED = """Закрепил чат за группой {}"""

CHAT_IS_LINKED = """Чат закреплен за группой {}"""

GROUP_CHAT_VIOLATION = """За этой группой уже закреплен чат! Пока!"""

####################### ФАЙЛ #######################

FILE_ATTACHED = """Куда сохранить файл {}?"""

FILE_SAVED = """Сохранил файл в {}."""

####################### ЗАГРУЗКА РАСПИСАНИЯ #######################

NOT_SCHEDULE_FORMAT = """Чет не похоже на расписание..."""

SCHEDULE_EXISTS = """Расписание с {start} по {end} уже загружено.\nОбновить?"""

DIDNT_PARSE = """Не удалось считать информацию:("""

SCHEDULE_UPLOADED = """Расписание загружено"""

SCHEDULE_UPDATED = """Обновил расписание"""

KEEP_SCHEDULE = """Оставил актуально расписание без изменений"""

####################### ПОКАЗ РАСПИСАНИЯ #######################

SCHEDULE_NOT_AVAILABLE = """Расписание доступно только в [личных чатах](https://t.me/@KonstantinSergeevichBot)"""

SCHEDULE = """Расписание на сегодня\n"""

SCHEDULE_RESULTS = """**{day_of_week}** {date}"""

FREE_DAY = """Нет занятий!"""

NO_SCHEDULE = """Пока нет расписания:("""

NO_NEXT_SCHEDULE = """На следующую неделю пока нет расписания(\nЖдем..."""

NO_PREV_SCHEDULE = """На предыдущую неделю нет расписания"""

####################### БИБЛИОТЕКА #######################

NO_LIBRARY_YET = """
Эта команда пока неактивна, но совсем скоро здесь будет доступ к учебным материалам.
"""

USER_GROUP_NOT_REGISTER = """
Доступ к учебнымм материалам доступен только для пользователей чьи группы зарегистрировали бота в чате. Обратись к старосте. 
"""

####################### ЗАГРУЗКА В БИБЛИОТЕКУ #######################

CHOOSE_SUBJ = """По какому предмету:"""

CHOOSE_TYPE = """Что ты прикрепляешь?"""

CONFIRM_SUBJECT = """Сохранить этот файл как {} по предмету {}"""

CONFIRM_SUBJECT_OK = """Сохранил {} по предмету {}"""