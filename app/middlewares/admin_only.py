from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import settings
from app.utils.texts import NO_ACCESS


class AdminOnlyMiddleware(BaseMiddleware):
    """Blocks any interaction from users who are not in the admin list."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        user_id = user.id if user else None

        if user_id is None or user_id not in settings.admin_ids:
            if isinstance(event, Message):
                await event.answer(NO_ACCESS)
            elif isinstance(event, CallbackQuery):
                await event.answer(NO_ACCESS, show_alert=True)
            return None

        return await handler(event, data)
