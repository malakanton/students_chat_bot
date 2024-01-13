from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import F
from app.loader import db
import datetime


cb_user_filter = F.message.chat.type == 'private'
GroupFilter = F.chat.type.in_({'group', 'supergroup'})
cb_group_filter = F.message.chat.type.in_({'group', 'supergroup'})


class UserFilter(BaseFilter):
    def __init__(self, users_ids: set[int] = None) -> None:
        self.users_ids = users_ids

    async def __call__(self, message: Message):
        if isinstance(self.users_ids, set):
            return (
                    message.chat.type == 'private' and
                    message.from_user.id in self.users_ids
            )
        else:
            return message.chat.type == 'private'


class SupportFilter(BaseFilter):
    async def __call__(self, message: Message):
        if '#support' in message.text:
            date = message.date + datetime.timedelta(hours=3)
            return {
                'text': message.text,
                'user_id': message.from_user.id,
                'user_name': message.from_user.username,
                'date': date.strftime('%Y-%m-%d %H:%M')
            }


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
