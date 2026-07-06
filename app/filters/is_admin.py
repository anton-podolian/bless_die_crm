from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from app.config import settings


class IsAdmin(BaseFilter):
    """Extra safety check that can be attached directly to sensitive handlers."""

    async def __call__(self, event: TelegramObject, event_from_user=None) -> bool:
        user = event_from_user
        if user is None:
            user = getattr(event, "from_user", None)
        return bool(user and user.id in settings.admin_ids)
