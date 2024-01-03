from aiogram.dispatcher.filters.state import StatesGroup, State


class FileAttached(StatesGroup):
    FileType = State()
    Approval = State()