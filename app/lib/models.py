from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import List, Optional, Set
import datetime as dt
from config import ADMIN_CHAT


from keyboards.buttons import codes
from lib.dicts import ru_days, ru_days_inv


@dataclass
class Users:
    admins: set[int] = Field(default=set())
    heads: set[int] = Field(default=set())
    regular: set[int] = Field(default=set())
    unreg: set[int] = Field(default=set())


@dataclass
class Group:
    id: int
    name: str
    course: int
    chat_id: Optional[int]


@dataclass
class Groups:
    groups: List[Group]
    chats: Optional[Set[int]] = Field(default=set())
    courses: Optional[List[int]] = Field(default=list())

    def __post_init__(self):
        self.groups = sorted(self.groups, key=lambda group: group.id)
        self.chats = set([group.chat_id for group in self.groups if group.chat_id])|set([int(ADMIN_CHAT)])
        self.courses = sorted(list(set([group.course for group in self.groups])))


@dataclass
class Today:
    date: dt.date
    week: int
    day_of_week: int
    name: str = Field(default='')

    def __post_init__(self):
        self.name = ru_days_inv.get(self.day_of_week, 'Воскресенье')


@dataclass
class Lesson:
    subj: str
    start: dt.time
    end: dt.time
    teacher: str
    loc: str


@dataclass
class DayOfWeek:
    id: int
    name: str
    code: str
    date: dt.date
    free: bool = Field(default=True)
    schedule: Optional[List[Lesson]] = Field(default=list())


@dataclass
class Week:
    num: int
    days: list = Field(default_factory=lambda: list())

    def __post_init__(self):
        for day, i in ru_days.items():
            date = dt.date.fromisocalendar(dt.datetime.now().year, self.num, i)
            code = codes[i - 1]
            self.days.append(DayOfWeek(i, day, code, date))

    def get_all_active(self):
        return [item for item in self.days if not item.free]

    def get_day(self, day_id: int):
        return self.days[day_id-1]
