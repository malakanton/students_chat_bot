from fastapi import FastAPI
from api.endpoints.config import config_router

http_app = FastAPI()

http_app.include_router(config_router, prefix="/config")


@http_app.get("/")
async def read_root():
    return {"health_check": "ok"}
