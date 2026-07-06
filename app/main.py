from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from app.config import settings
from app.handlers import router as root_router
from app.middlewares import AdminOnlyMiddleware, DbSessionMiddleware, ThrottlingMiddleware
from app.utils.texts import GENERIC_ERROR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def on_error(event: ErrorEvent) -> None:
    logger.exception("Unhandled error while processing update", exc_info=event.exception)
    update = event.update
    try:
        if update.message is not None:
            await update.message.answer(GENERIC_ERROR)
        elif update.callback_query is not None:
            await update.callback_query.answer(GENERIC_ERROR, show_alert=True)
    except Exception:
        logger.exception("Failed to notify user after an unhandled error")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(AdminOnlyMiddleware())
    dp.update.outer_middleware(DbSessionMiddleware())

    dp.include_router(root_router)
    dp.errors.register(on_error)

    return dp


async def main() -> None:
    if not settings.admin_ids:
        logger.warning("No ADMIN_ID_* configured - nobody will be able to use this bot!")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    except TelegramNetworkError:
        logger.exception("Network error while polling Telegram")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
