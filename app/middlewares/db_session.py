from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.exc import SQLAlchemyError

from app.database.engine import async_session_factory
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.utils.texts import DB_ERROR

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """Opens an async DB session per update and injects an OrderService.

    On any database error the transaction is rolled back and a friendly
    message is shown instead of letting the bot crash.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            async with async_session_factory() as session:
                repository = OrderRepository(session)
                data["session"] = session
                data["order_service"] = OrderService(repository)
                try:
                    result = await handler(event, data)
                    await session.commit()
                    return result
                except SQLAlchemyError:
                    await session.rollback()
                    raise
        except SQLAlchemyError:
            logger.exception("Database error while handling update")
            await self._notify_user(event, DB_ERROR)
            return None

    @staticmethod
    async def _notify_user(event: TelegramObject, text: str) -> None:
        try:
            if hasattr(event, "message") and event.message is not None:
                await event.message.answer(text)
            elif hasattr(event, "answer"):
                await event.answer(text)
        except Exception:
            logger.exception("Failed to notify user about DB error")
