from typing import Optional, List, Set
from enum import Enum
from pydantic import Field
from pydantic.dataclasses import dataclass

from lib.config.config import cfg


class StudyForm(Enum):
    INT = 1
    EXT = 0

@dataclass
class Group:
    id: int
    name: str
    course: int
    study_form: int
    chat_id: Optional[int] = Field(default=None)
    gc_linc: Optional[str] = Field(default=None)


@dataclass
class Groups:
    groups: List[Group]
    chats: Optional[Set[int]] = Field(default=set())
    courses: Optional[List[int]] = Field(default=list())

    def __post_init__(self):
        self.groups = sorted(self.groups, key=lambda group: group.id)
        self._set_chats()
        self._set_courses()

    def _set_chats(self):
        self.chats = set(
            [group.chat_id for group in self.groups if group.chat_id]
        ) | set([int(cfg.secrets.ADMIN_CHAT)])

    def _set_courses(self):
        self.courses = sorted(list(set([group.course for group in self.groups])))

    def filter_study_type(self, form: int):
        self.groups = [g for g in self.groups if g.study_form == form]
        self._set_courses()
        self._set_courses()
