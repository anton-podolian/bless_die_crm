from __future__ import annotations

from datetime import datetime, timezone
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
        )

    async def get_order(self, order_id: int) -> Order | None:
        return await self.repository.get_by_id(order_id)

    async def update_field(self, order: Order, field: str, value: Any) -> Order:
        return await self.repository.update(order, **{field: value})

    async def close_order(self, order: Order) -> Order:
        return await self.repository.update(
            order,
            status=OrderStatus.SOLD,
            closed_at=datetime.now(timezone.utc),
        )

    async def reopen_order(self, order: Order) -> Order:
        return await self.repository.update(
            order,
            status=OrderStatus.IN_PROGRESS,
            closed_at=None,
        )

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
