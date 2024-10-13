from aiogram.fsm.state import State, StatesGroup


class FileAttached(StatesGroup):
    FileType = State()
    Approval = State()


class PushNotoficationsState(StatesGroup):
    set_time = State()


class StartUser(StatesGroup):
    choose_role = State()
    choose_teacher = State()
    teacher_confirm = State()
    choose_study_form = State()
    choose_course = State()
    choose_group = State()
    confirm = State()
