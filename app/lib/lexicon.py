
HELP_MSG = """
__Команды бота__

📅*/schedule* - посмотреть расписание
⏰*/notifications* - настройка уведомлений
📗*/library* - учебные материалы
📋*/description* - про бота
📨*/contacts* - обратная связь
"""


DESCRIPTION = """
🐱 Я - котэ КТ МТУСИ, который помогает студентам очно-заочного отделения.

🔹Только попроси - и я покажу тебе расписание.

🔹Если захочешь, могу уведомлять тебя за несколько минут до предстоящего занятия, для этого выбери команду /notifications.

🔹В групповом чате можешь вызвать команду /summary и я перескажу что обсуждалось если у тебя нет времени перечитывать.

🔹А когда совсем вырасту, буду собирать и помогу тебе быстро находить материалы по учебным предметам из твоей группы (тексты лекций и шаблоны конспектов, тексты домашних заданий).

🔹Расписание для твоей группы в Google Calendars доступно по [ссылке]<LINK>({}<LINK>)

В левом нижнем углу ты найдешь меню моих команд.↙️
"""

CONTACTS = """
Для обратной связи напиши здесь свое сообщение и обязательно оставь в нем пометку #support.
"""

MAIN_MENU = {
    '/help': '❔ помощь',
    '/schedule': '📅 посмотреть расписание',
    '/notifications': '⏰ настройка уведомлений',
    '/library': '📚учебные материалы'
}

REPLY_SUPPORT = """
Спасибо за обращение! 🫡
 
Я передал это сообщение в команду разработки, они проверят его как только будет возможность.
"""

FORWARD_SUPPORT = """
{date}
Обращение от {first_name} @{username} ({user_id}), группа {group_name}:

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

DIDNT_SAVE_FILE = """ОК, документ не сохранен."""

####################### ЗАГРУЗКА РАСПИСАНИЯ #######################

NOT_SCHEDULE_FORMAT = """Этот файл не похож на расписание. Перепроверь пожалуйста :)"""

SCHEDULE_EXISTS = """Расписание с {start} по {end} уже загружено.\nОбновить?"""

DIDNT_PARSE = """Не удалось считать информацию..🥴"""

SCHEDULE_UPLOADED = """Расписание загружено✅"""

SCHEDULE_UPDATED = """Обновил расписание✅"""

KEEP_SCHEDULE = """ОК, просто считаем старое расписание актуальным."""

####################### ПОКАЗ РАСПИСАНИЯ #######################

SCHEDULE_NOT_AVAILABLE = """Расписание доступно только в [личных чатах]<LINK>(https://t.me/@KoteMTUCIbot<LINK>)"""

SCHEDULE_FOR_DETAIL = """Больше информации по расписанию в [личных чатах]<LINK>(https://t.me/@KoteMTUCIbot<LINK>)"""

SCHEDULE = """Расписание на сегодня\n"""

WEEK_SCHEDULE = """🗓Расписание на неделю с """

SCHEDULE_RESULTS = """**{day_of_week}** {date}"""

FREE_DAY = """Нет занятий!"""

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

####################### УВЕДОМЛЕНИЯ #######################

NOTIF = """
⏰⏰⏰
❗️Через {minutes} минут начнется занятие❗️
*{subject}* 
{teacher}
{start} - {end}
{link}
"""

NO_LINK_YET = """Пока нет ссылки"""

LINK_PHRASE = """Ссылка на занятие"""

NOTIFICATIONS_STATUS = """
Уведомления: *{}*
"""

NOTIFICATIONS_ON = """
За {} минут до занятия я буду присылать сообщение с деталями занятия и ссылкой, если она у меня есть.
Уведомления работают только в будние дни.
"""

NOTIFICATIONS_ON_BEGIN = """
Можешь поменять настройки кнопками ниже.
"""

NOTIFICATIONS_OFF = """
Чтобы включить уведомления, выбери ниже за сколько минут оповещать тебя о предстоящем занятии:
"""

NOTIFICATIONS_ON_OFF_END = """
Когда захочешь поменять настройки уведомлений, снова вызови команду /notifications
"""

NOTIF_FLAG = [
    '🔴Выключены',
    '🟢Включены'
]

####################### ПРИКРЕПЛЕНИЕ ССЫЛКИ #######################

LINK_POSTED = """Похоже на ссылку на занятие, сохранить?"""

LINK_UPDATED = """Добавил ссылку!"""

####################### GPT #######################

NO_SUMMARY = """Ой, не получилось сделать сводку..."""

BAD_TEXT_FROM_GPT = """Ой, не получилось напечатать ответ.."""

COLLECTION_UPDATED = """Обновил базу знаний!"""

COLLECTION_NOT_UPDATED = """Не удалось обновить базу знаний("""
