from enum import Enum

COURSES = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣"}


class Start(Enum):
    TEACHER = 'Преподаватель'
    STUDENT = 'Студент'


class StudyFormKb(Enum):
    INTRAMURAL = "Очная"
    EXTRAMURAL = "Заочная"


class Confirm(Enum):
    OK = "✅Да!"
    CANCEL = "❌Назад"


class FileButt(Enum):
    CANCEL = "❌Не сохраняй"
    STUDY = "📗Сохрани"
    SCHEDULE = "Расписание"


class SchdUpdButt(Enum):
    UPDATE = "✅Обнови"
    KEEP = "❌Не обновляй"


class FileTypeButt(Enum):
    LECTURE = "Лекцию"
    BLANK = "Шаблон"
    TASK = "Задание"
    HOMEWORK = "Домашку"
    ADDITIONAL = "Доп материалы"


class CancelButt(Enum):
    CANCEL = "❌Отмена"
    BACK = "⬅Назад"


class ScheduleButt(Enum):
    BACK = "⬅️"
    WEEK = "Вся неделя"
    FORW = "➡️"


class TeachersButt(Enum):
    LEFT = "⬅️"
    RIGHT = "➡️"


class SwitchNotif(Enum):
    ON = "⏰{}'"
    OFF = "🟥OFF"
    SET = "Установить время уведомлений ⏰"


class NewsLetter(Enum):
    OK = "✅Отправить!"
    CANCEL = "❌Отмена"


codes = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]


class NotifMenuBut(Enum):
    ADVANCE = "Напоминалки перед парой"
    DAILY = "Ежедневные оповещения"
