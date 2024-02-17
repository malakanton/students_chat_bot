from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import F
from loader import db
import datetime
import re


GroupFilter = F.chat.type.in_({'group', 'supergroup'})
cb_user_filter = F.message.chat.type == 'private'
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
        if message.text:
            if '#support' in message.text:
                date = message.date + datetime.timedelta(hours=3)
                return {
                    'text': message.text,
                    'user_id': message.from_user.id,
                    'first_name': message.from_user.first_name,
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


class LessonLinkFilter(BaseFilter):
    def __init__(self) -> None:
        self.pattern = re.compile(r'https?://(?:telemost.*\b|\w+\.zoom\.us.*\b|meet\.google\.com)\b')

    async def __call__(self, message: Message) -> bool:
        if message.text:
            search_result = re.findall(self.pattern, message.text)
            if search_result:
                return {
                    'link': search_result[0]
                }
