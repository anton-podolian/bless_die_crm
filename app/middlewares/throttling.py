from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

THROTTLE_SECONDS = 0.7


class ThrottlingMiddleware(BaseMiddleware):
    """Ignores duplicate callback taps that arrive within a short window."""

    def __init__(self) -> None:
        self._last_seen: dict[tuple[int, str], float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            key = (user_id, event.data or "")
            now = time.monotonic()
            last = self._last_seen.get(key)
            if last is not None and (now - last) < THROTTLE_SECONDS:
                await event.answer()
                return None
            self._last_seen[key] = now

        return await handler(event, data)
