from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo
from typing import Any

from app.models.order import Order, OrderStatus
from app.repositories.order_repository import (
    OrderRepository,
    OrderStats,
    SortOption,
    StatusFilter,
)


class OrderService:
    """Business logic for working with orders."""

    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    async def create_order(self, data: dict[str, Any]) -> Order:
        return await self.repository.create(
            photo_file_id=data.get("photo_file_id"),
            title=data["title"],
            size=data["size"],
            buy_price=data["buy_price"],
            sell_price=data["sell_price"],
            customer=data.get("customer"),
            comment=data.get("comment"),
            status=OrderStatus.IN_PROGRESS,
            is_ordered=False,
            created_at=datetime.now(UTC),
        )

    async def get_order(self, order_id: int) -> Order | None:
        return await self.repository.get_by_id(order_id)

    async def update_field(self, order: Order, field: str, value: Any) -> Order:
        return await self.repository.update(order, **{field: value})

    async def close_order(self, order: Order) -> Order:
        return await self.repository.update(
            order,
            status=OrderStatus.SOLD,
            closed_at=datetime.now(UTC),
        )

    async def reopen_order(self, order: Order) -> Order:
        return await self.repository.update(
            order,
            status=OrderStatus.IN_PROGRESS,
            closed_at=None,
        )

    async def toggle_ordered(self, order: Order) -> Order:
        """Toggle whether an in-progress item's purchase has been placed."""
        if order.status != OrderStatus.IN_PROGRESS:
            return order
        return await self.repository.update(order, is_ordered=not order.is_ordered)

    async def delete_order(self, order: Order) -> None:
        await self.repository.delete(order)

    async def duplicate_order(self, order: Order) -> Order:
        return await self.repository.create(
            photo_file_id=order.photo_file_id,
            title=order.title,
            size=order.size,
            buy_price=order.buy_price,
            sell_price=order.sell_price,
            customer=order.customer,
            comment=order.comment,
            status=OrderStatus.IN_PROGRESS,
            is_ordered=False,
            created_at=datetime.now(UTC),
        )

    async def get_last_order(self) -> Order | None:
        return await self.repository.get_last()

    async def list_orders(
        self, page: int, status_filter: StatusFilter, sort: SortOption
    ) -> tuple[list[Order], int]:
        return await self.repository.list_page(page=page, status_filter=status_filter, sort=sort)

    async def search_orders(self, query: str, page: int = 0) -> tuple[list[Order], int]:
        return await self.repository.search(query=query, page=page)

    async def get_stats(self) -> OrderStats:
        return await self.repository.get_stats()

    async def get_month_stats(self, year: int, month: int) -> OrderStats:
        """Return stats for orders created in a Kyiv calendar month."""
        if not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        kyiv = ZoneInfo("Europe/Kyiv")
        start = datetime(year, month, 1, tzinfo=kyiv)
        end = (
            datetime(year + 1, 1, 1, tzinfo=kyiv)
            if month == 12
            else datetime(year, month + 1, 1, tzinfo=kyiv)
        )
        return await self.repository.get_stats_for_period(
            start=start.astimezone(UTC), end=end.astimezone(UTC)
        )
