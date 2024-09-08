import datetime as dt
from typing import Optional, List

from pydantic import Field
from pydantic.dataclasses import dataclass

from keyboards.buttons import codes
from lib.dicts import RU_DAYS, RU_DAYS_INV


@dataclass
class Lesson:
    subj: str
    start: dt.datetime
    end: dt.datetime
    loc: str
    teacher: str = Field(default='')
    group_name: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)
    comment: Optional[str] = Field(default=None)
    special_case: Optional[str] = Field(default=None)
    whole_day: Optional[bool] = Field(default=False)


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
    days: List[Optional[DayOfWeek]] = Field(default_factory=list)

    def __init__(self, num: int):
        self.num = num

    def __post_init__(self):
        for day, i in RU_DAYS.items():
            date = dt.date.fromisocalendar(dt.datetime.now().year, self.num, i)
            code = codes[i - 1]
            self.days.append(DayOfWeek(i, day, code, date))

    def get_all_active(self):
        return [item for item in self.days if not item.free]

    def get_day(self, day_id: int):
        return self.days[day_id - 1]

    def map_lessons(self, lessons: List[Lesson]):
        lessons_map = {}

        for l in lessons:
            day_num = l.start.isocalendar()[2]
            lessons_map[day_num] = lessons_map.get(day_num, []) + [l]

        for day in self.days:
            day_lessons = lessons_map.get(day.id, [])
            if day_lessons:
                day.schedule = day_lessons
                day.free = False


@dataclass
class Today:
    date: dt.date
    week: int
    day_of_week: int
    name: str = Field(default="")

    def __post_init__(self):
        self.name = RU_DAYS_INV.get(self.day_of_week, "Воскресенье")
