

HELP_MSG = """
__Команды бота__

📅*/schedule* - посмотреть расписание
📗*/library* - учебные материалы
📋*/description* - про бота
📨*/contacts* - обратная связь
"""


DESCRIPTION = """
🐱 Я - котэ КТ МТУСИ, который помогает студентам очно-заочного отделения.

🔹Только попроси - и я покажу тебе расписание.

🔹Когда немного подрасту, стану уведомлять о загрузке нового расписания.

🔹А когда совсем вырасту, буду собирать и помогу тебе быстро находить материалы по учебным предметам из твоей группы (тексты лекций и шаблоны конспектов, тексты домашних заданий).

В левом нижнем углу ты найдешь меню моих команд.↙️
"""

CONTACTS = """
Для обратной связи напиши здесь свое сообщение и обязательно оставь в нем пометку #support.
"""

MAIN_MENU = {
    '/help': '❔ помощь',
    '/schedule': '📅 посмотреть расписание',
    '/library': '📚 учебные материалы'
}

REPLY_SUPPORT = """
Спасибо за обращение! 🫡
 
Я передал это сообщение в команду разработки, они проверят его как только будет возможность.
"""

FORWARD_SUPPORT = """
{date}
Обращение от @{username} ({user_id}), группа {group_name}:

{text}    
    """


####################### РЕГИСТРАЦИЯ #######################

HELLO = """
Привет, *{}*! 👋

Я котобот очно-заочного отделения КТ МТУСИ.
Давай сначала зарегистрируем тебя!
"""

COURSE_CHOICE = """На каком ты курсе?"""

GROUP_CHOICE = """А группа какая?"""

YOURE_REGISTERED = """Ты уже в группе {}"""

GROUP_CONFIRM = """Выбрана группа *{}* \nВсе правильно?"""

ADDED_TO_GROUP = """Итак, {}, теперь ты в группе *{}*!🎉🎉🎉
"""

NOT_REGISTERED = """Эй, сначала надо зарегистрироваться! для этого жмакни на /start"""

GROUP_LINKED = """Закрепил чат за группой {}"""

CHAT_IS_LINKED = """Чат закреплен за группой {}"""

GROUP_CHAT_VIOLATION = """За этой группой уже закреплен чат! Пока!"""

####################### ФАЙЛ #######################

FILE_ATTACHED = """Куда сохранить файл {}?"""

FILE_SAVED = """Сохранил файл в {}."""

DIDNT_SAVE_FILE = """ОК, документ НЕ сохранен."""

####################### ЗАГРУЗКА РАСПИСАНИЯ #######################

NOT_SCHEDULE_FORMAT = """Этот файл не похож на расписание. Перепроверь пожалуйста :)"""

SCHEDULE_EXISTS = """Расписание с {start} по {end} уже загружено.\nОбновить?"""

DIDNT_PARSE = """Не удалось считать информацию..🥴"""

SCHEDULE_UPLOADED = """Расписание загружено✅"""

SCHEDULE_UPDATED = """Обновил расписание✅"""

KEEP_SCHEDULE = """ОК, просто считаем старое расписание актуальным."""

####################### ПОКАЗ РАСПИСАНИЯ #######################

SCHEDULE_NOT_AVAILABLE = """Расписание доступно только в [личных чатах](https://t.me/@KoteMTUCIbot)"""

SCHEDULE = """Расписание на сегодня\n"""

SCHEDULE_RESULTS = """**{day_of_week}** {date}"""

FREE_DAY = """Нет занятий"""

NO_SCHEDULE = """Пока нет расписания😕"""

NO_NEXT_SCHEDULE = """На следующую неделю пока нет расписания(\nЖдем..."""

NO_PREV_SCHEDULE = """На предыдущую неделю нет расписания"""

####################### БИБЛИОТЕКА #######################

NO_LIBRARY_YET = """
Эта команда пока неактивна, но совсем скоро здесь будет доступ к учебным материалам. ⏳
"""

USER_GROUP_NOT_REGISTER = """
Доступ к учебнымм материалам доступен только для пользователей чьи группы зарегистрировали бота в чате. Обратись к старосте. 🤓 
"""

####################### ЗАГРУЗКА В БИБЛИОТЕКУ #######################

CHOOSE_SUBJ = """По какому предмету:"""

CHOOSE_TYPE = """Что ты прикрепляешь?"""

CONFIRM_SUBJECT = """Сохранить этот файл как {} по предмету {} ?"""

CONFIRM_SUBJECT_OK = """Сохранил {} по предмету \n{}."""


####################### БОЛТАЛКА #######################

TEXT_REPLY = """Я просто бот-кот, и пока не могу тебе ответить. Но очень хочу! 😸"""