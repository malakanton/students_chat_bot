from pydantic import Field, BaseModel
from pydantic.dataclasses import dataclass
from typing import List, Optional
import datetime as dt


ru_days = [
    'Понедельник',
    'Вторник',
    'Среда',
    'Черверг',
    'Пятница',
    'Суббота'
]

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
        for i, day in zip(range(1, 7), ru_days):
            self.days[i] = DayOfWeek(i, day)

    def get_all_active(self):
        return [item for item in self.days if not item.free]

    def get_day(self, day_id: int):
        return self.days.get(day_id, None)
w = Week(num=1)
print(w.__dict__)
print(w.days[1])
