from fastapi import APIRouter
from lib.config.config import cfg

config_router = APIRouter()


@config_router.get("/")
async def config():
    return cfg.dict()
