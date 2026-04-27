import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI

from bot.handlers import common, photo, start
from bot.middlewares import DbSessionMiddleware
from core.config import config
from db.database import SessionLocal, engine
from db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)

dp.update.middleware(DbSessionMiddleware(session_pool=SessionLocal))
dp.include_router(start.router)
dp.include_router(photo.router)
dp.include_router(common.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await bot.set_webhook(url=config.WEBHOOK_URL)
    yield
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}
