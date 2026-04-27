from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser

from core.i18n import I18n
from db import crud


class SimpleI18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: TelegramUser = data.get("event_from_user")
        session = data.get("session")

        lang = "en"
        if user:
            db_user = await crud.get_user(session, user.id)
            if db_user:
                lang = db_user.language
            else:
                lang = (
                    user.language_code if user.language_code in ["uk", "en"] else "en"
                )

        data["i18n"] = I18n(lang)
        return await handler(event, data)
