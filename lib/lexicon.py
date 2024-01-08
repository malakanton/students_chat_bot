

HELP_MSG = """
__Описание бота__
_Здесь должно быть описание_

__Команды бота__
🔄*/start* - регистрация
📨*/contacts* - контакты
📋*/description* - про бота
📅*/schedule* - посмотреть расписание
📗*/library* - учебные материалы
"""


####################### РЕГИСТРАЦИЯ #######################

HELLO = """
Привет, *{}*\!

Я бот 

На каком ты курсе?
"""

GROUP_CHOICE = """А группа какая?"""

YOURE_REGISTERED = """Ты уже в группе {}"""

ADDED_TO_GROUP = """Отлично, добавил тебя в группу *{}*.
Теперь когда попросишь показать расписание, я буду показывать расписание для твоей группы.
Если хочешь посмотреть расписание других групп, то нам с тобой не по пути. 
"""

NOT_REGISTERED = """Эй, начала надо зарегистрироваться\! для этого жмакни на /start"""

GROUP_LINKED = """Закрепил чат за группой {}"""

CHAT_IS_LINKED = """Чат закреплен за группой {}"""

GROUP_CHAT_VIOLATION = """За этой группой уже закреплен чат! Пока!"""

####################### ФАЙЛ #######################

FILE_ATTACHED = """Куда сохранить файл {}?"""

FILE_SAVED = """Сохранил файл в {}."""

####################### ЗАГРУЗКА РАСПИСАНИЯ #######################

NOT_SCHEDULE_FORMAT = """чет не похоже на расписание..."""

SCHEDULE_EXISTS = """Расписание с {start} по {end} уже загружено.\nОбновить?"""

DIDNT_PARSE = """Не удалось считать информацию:("""

SCHEDULE_UPLOADED = """Расписание загружено"""

SCHEDULE_UPDATED = """Обновил расписание"""

KEEP_SCHEDULE = """Расписание оставил как было"""

####################### ПОКАЗ РАСПИСАНИЯ #######################

SCHEDULE = """Расписание на сегодня\n"""

SCHEDULE_RESULTS = """**{day_of_week}** {date}"""

FREE_DAY = """Нет занятий!"""

NO_SCHEDULE = """Пока нет расписания:("""

NO_NEXT_SCHEDULE = """На следующую неделю пока нет расписания("""

NO_PREV_SCHEDULE = """На предыдущую неделю нет расписания"""