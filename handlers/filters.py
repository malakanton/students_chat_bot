from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import F
from loader import db


user_filter = F.chat.type == 'private'
cb_user_filter = F.message.chat.type == 'private'
group_filter = F.chat.type.in_({'group', 'supergroup'})
cb_group_filter = F.message.type.in_({'group', 'supergroup'})


class IsRegisteredGroup(BaseFilter):
    def __init__(self, group_ids: set[int]) -> None:
        self.group_ids = group_ids

    async def __call__(self, message: Message):
        return message.chat.id in self.group_ids


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[str]) -> None:
        self.admin_ids = list(map(int, admin_ids))

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

class UnRegisteredUser(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return db.get_user_group(message.from_user.id) == None
