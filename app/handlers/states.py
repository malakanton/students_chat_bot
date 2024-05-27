from aiogram.fsm.state import State, StatesGroup


class FileAttached(StatesGroup):
    FileType = State()
    Approval = State()


class PushNotoficationsState(StatesGroup):
    set_time = State()
