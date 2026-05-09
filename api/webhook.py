import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI

from bot.handlers import common, history, photo, settings, start
from bot.i18n_middleware import SimpleI18nMiddleware
from bot.middlewares import DbSessionMiddleware
from core.config import config
from db.database import SessionLocal, engine
from db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)

dp.update.middleware(DbSessionMiddleware(session_pool=SessionLocal))
dp.update.middleware(SimpleI18nMiddleware())

dp.include_router(common.router)
dp.include_router(history.router)
dp.include_router(settings.router)
dp.include_router(start.router)
dp.include_router(photo.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Setting Telegram webhook to %s", config.WEBHOOK_URL)
    await bot.set_webhook(url=config.WEBHOOK_URL)
    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
@app.post("/webhook/webhook")
async def telegram_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}
