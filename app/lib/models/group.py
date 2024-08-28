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
    chat_id: Optional[int] = Field(default=None)
    gc_linc: Optional[str] = Field(default=None)


@dataclass
class Groups:
    groups: List[Group]
    chats: Optional[Set[int]] = Field(default=set())
    courses: Optional[List[int]] = Field(default=list())

    def __post_init__(self):
        self.groups = sorted(self.groups, key=lambda group: group.id)
        self.chats = set(
            [group.chat_id for group in self.groups if group.chat_id]
        ) | set([int(cfg.secrets.ADMIN_CHAT)])
        self.courses = sorted(list(set([group.course for group in self.groups])))
