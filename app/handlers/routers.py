from aiogram import Router
from .filters import UserFilter, GroupFilter


users_router = Router()
groups_router = Router()
users_router.message.filter(UserFilter())
groups_router.message.filter(GroupFilter)
