from pydantic import Field
from pydantic.dataclasses import dataclass

from typing import Optional


@dataclass
class Users:
    admins: set = Field(default_factory=set)
    heads: set = Field(default_factory=set)
    regular: set = Field(default_factory=set)
    unreg: set = Field(default_factory=set)
    allowed: set = Field(default_factory=set)
    teachers: set = Field(default_factory=set)

    def update(self, db):
        self.admins = db.get_users_ids("admin")
        self.heads = db.get_users_ids("head")
        self.regular = db.get_users_ids("regular")
        self.unreg = db.get_users_ids("unreg")
        self.teachers = db.get_users_ids("teacher")
        self.allowed = db.get_users_ids("allowed")


@dataclass
class User:
    id: int
    name: str
    tg_login: Optional[str]
    role: str
    notifications: Optional[int] = Field(default=None)
    group_id: Optional[int] = Field(default=None)
    teacher_id:  Optional[int] = Field(default=None)

    def is_teacher(self):
        return self.teacher_id is not None


@dataclass
class Teacher:
    id: int
    last_name: str
    initials: str
    fathers_name: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    tg_id: int = Field(default=0)
