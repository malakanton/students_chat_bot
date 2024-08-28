from pydantic import Field
from pydantic.dataclasses import dataclass

from typing import Optional


@dataclass
class Users:
    admins: set[int] = Field(default=set())
    heads: set[int] = Field(default=set())
    regular: set[int] = Field(default=set())
    unreg: set[int] = Field(default=set())
    allowed: set[int] = Field(default=set())

@dataclass
class User:
    id: int
    name: str
    tg_login: str
    role: str
    notifications: Optional[int] = Field(default=None)
    group_id: Optional[int] = Field(default=None)
    ext_teacher_id:  Optional[int] = Field(default=None)
    int_teacher_id: Optional[int] = Field(default=None)

    def is_teacher(self):
        return self.teacher_id is not None


@dataclass
class Teacher:
    id: int
    name: str
    tg_id: int = Field(default=0)
    code: str = Field(default='')
