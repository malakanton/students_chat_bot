import datetime as dt
from typing import List, Optional, Set

from config import ADMIN_CHAT
from keyboards.buttons import codes
from lib.dicts import RU_DAYS, RU_DAYS_INV
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Users:
    admins: set[int] = Field(default=set())
    heads: set[int] = Field(default=set())
    regular: set[int] = Field(default=set())
    unreg: set[int] = Field(default=set())
    allowed: set[int] = Field(default=set())


@dataclass
class Group:
    id: int
    name: str
    course: int
    chat_id: Optional[int]
    gc_linc: Optional[str]


@dataclass
class Groups:
    groups: List[Group]
    chats: Optional[Set[int]] = Field(default=set())
    courses: Optional[List[int]] = Field(default=list())

    def __post_init__(self):
        self.groups = sorted(self.groups, key=lambda group: group.id)
        self.chats = set(
            [group.chat_id for group in self.groups if group.chat_id]
        ) | set([int(ADMIN_CHAT)])
        self.courses = sorted(list(set([group.course for group in self.groups])))


@dataclass
class Today:
    date: dt.date
    week: int
    day_of_week: int
    name: str = Field(default="")

    def __post_init__(self):
        self.name = RU_DAYS_INV.get(self.day_of_week, "Воскресенье")


@dataclass
class Lesson:
    subj: str
    start: dt.time
    end: dt.time
    teacher: str
    loc: str
    link: Optional[str] = Field(default=None)
    comment: Optional[str] = Field(default=None)


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
        for day, i in RU_DAYS.items():
            date = dt.date.fromisocalendar(dt.datetime.now().year, self.num, i)
            code = codes[i - 1]
            self.days.append(DayOfWeek(i, day, code, date))

    def get_all_active(self):
        return [item for item in self.days if not item.free]

    def get_day(self, day_id: int):
        return self.days[day_id - 1]


@dataclass
class File:
    subj_id: int
    subj_name: str
    file_type: str
    file_name: str
    s3_path: str = Field(default_factory=str)

    def __post_init__(self):
        self.s3_path = f"{self.subj_name}/{self.file_type}/{self.file_name}"
