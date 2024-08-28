import datetime as dt
from typing import Optional, List

from pydantic import Field
from pydantic.dataclasses import dataclass

from keyboards.buttons import codes
from lib.dicts import RU_DAYS, RU_DAYS_INV


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
class Today:
    date: dt.date
    week: int
    day_of_week: int
    name: str = Field(default="")

    def __post_init__(self):
        self.name = RU_DAYS_INV.get(self.day_of_week, "Воскресенье")
