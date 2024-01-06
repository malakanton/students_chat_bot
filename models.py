from pydantic import Field, BaseModel
from pydantic.dataclasses import dataclass
from typing import List, Optional
import datetime as dt


ru_days = {
    'Понедельник': 1,
    'Вторник': 2,
    'Среда': 3,
    'Черверг': 4,
    'Пятница': 5,
    'Суббота': 6
}


@dataclass
class Group:
    id: int
    name: str
    course: int
    chat_id: Optional[int]


@dataclass
class Today:
    date: str
    week: int
    day_of_week: int


@dataclass
class Lesson:
    subj: str
    start: dt.datetime
    end: dt.datetime
    teacher: str
    loc: str


@dataclass
class DayOfWeek:
    id: int
    name: str
    free: bool = Field(default=True)
    schedule: Optional[List[Lesson]] = Field(default=list())
    date: str = Field(default='')

    def set_date(self, schedule):
        self.date = self.schedule[0].start.date()


@dataclass
class Week:
    num: int
    days: dict = Field(default_factory=lambda: dict())

    def __post_init__(self):
        for day, i in ru_days.items():
            self.days[i] = DayOfWeek(i, day)

    def get_all_active(self):
        return [item for item in self.days if not item.free]

    def get_day(self, day_id: int):
        return self.days.get(day_id, None)

