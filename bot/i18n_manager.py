from typing import Any, Optional

from aiogram.types import User as TelegramUser
from aiogram_i18n.managers import BaseManager

from db import crud


class UserI18nManager(BaseManager):
    async def get_locale(
        self, event_from_user: Optional[TelegramUser], session: Any = None
    ) -> str:
        if not event_from_user:
            return "en"

        if session:
            user = await crud.get_user(session, event_from_user.id)
            if user:
                return user.language

        user_lang = event_from_user.language_code
        return user_lang if user_lang in ["uk", "en"] else "en"

    async def set_locale(self, locale: str, session: Any = None) -> None:
        pass
