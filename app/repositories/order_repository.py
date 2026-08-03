from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus

PAGE_SIZE = 10


class SortOption(str, enum.Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    MOST_EXPENSIVE = "most_expensive"
    MOST_PROFIT = "most_profit"


class StatusFilter(str, enum.Enum):
    ALL = "all"
    IN_PROGRESS = "in_progress"
    SOLD = "sold"


@dataclass
class OrderStats:
    total_count: int
    in_progress_count: int
    sold_count: int
    total_buy: float
    total_sell: float
    total_profit: float
    average_profit: float


class OrderRepository:
    """Encapsulates all database access for the Order entity."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields: Any) -> Order:
        order = Order(**fields)
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self.session.get(Order, order_id)

    async def update(self, order: Order, **fields: Any) -> Order:
        for key, value in fields.items():
            setattr(order, key, value)
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def delete(self, order: Order) -> None:
        await self.session.delete(order)
        await self.session.flush()

    async def get_last(self) -> Order | None:
        stmt = select(Order).order_by(Order.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _apply_status_filter(self, stmt: Select, status_filter: StatusFilter) -> Select:
        if status_filter == StatusFilter.IN_PROGRESS:
            return stmt.where(Order.status == OrderStatus.IN_PROGRESS)
        if status_filter == StatusFilter.SOLD:
            return stmt.where(Order.status == OrderStatus.SOLD)
        return stmt

    def _apply_sort(self, stmt: Select, sort: SortOption) -> Select:
        if sort == SortOption.OLDEST:
            return stmt.order_by(Order.created_at.asc())
        if sort == SortOption.MOST_EXPENSIVE:
            return stmt.order_by(Order.sell_price.desc())
        if sort == SortOption.MOST_PROFIT:
            return stmt.order_by(Order.profit.desc())
        return stmt.order_by(Order.created_at.desc())

    async def list_page(
        self,
        page: int,
        status_filter: StatusFilter = StatusFilter.ALL,
        sort: SortOption = SortOption.NEWEST,
    ) -> tuple[list[Order], int]:
        base_stmt = select(Order)
        base_stmt = self._apply_status_filter(base_stmt, status_filter)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = self._apply_sort(base_stmt, sort)
        stmt = stmt.offset(page * PAGE_SIZE).limit(PAGE_SIZE)
        result = await self.session.execute(stmt)
        orders = list(result.scalars().all())
        return orders, total

    async def search(self, query: str, page: int = 0) -> tuple[list[Order], int]:
        pattern = f"%{query.strip()}%"
        conditions = [
            Order.title.ilike(pattern),
            Order.size.ilike(pattern),
            Order.customer.ilike(pattern),
        ]
        if query.strip().isdigit():
            conditions.append(Order.id == int(query.strip()))

        base_stmt = select(Order).where(or_(*conditions))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = base_stmt.order_by(Order.created_at.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
        result = await self.session.execute(stmt)
        orders = list(result.scalars().all())
        return orders, total

    async def get_stats(self) -> OrderStats:
        return await self.get_stats_for_period()

    async def get_stats_for_period(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> OrderStats:
        conditions = []
        if start is not None:
            conditions.append(Order.created_at >= start)
        if end is not None:
            conditions.append(Order.created_at < end)

        def filtered(stmt):
            return stmt.where(*conditions) if conditions else stmt

        total_count = (await self.session.execute(filtered(select(func.count(Order.id))))).scalar_one()
        in_progress_count = (
            await self.session.execute(
                filtered(select(func.count(Order.id))).where(Order.status == OrderStatus.IN_PROGRESS)
            )
        ).scalar_one()
        sold_count = (
            await self.session.execute(
                filtered(select(func.count(Order.id))).where(Order.status == OrderStatus.SOLD)
            )
        ).scalar_one()

        totals = (
            await self.session.execute(
                filtered(select(
                    func.coalesce(func.sum(Order.buy_price), 0),
                    func.coalesce(func.sum(Order.sell_price), 0),
                    func.coalesce(func.sum(Order.profit), 0),
                    func.coalesce(func.avg(Order.profit), 0),
                ))
            )
        ).one()

        total_buy, total_sell, total_profit, average_profit = totals

        return OrderStats(
            total_count=total_count,
            in_progress_count=in_progress_count,
            sold_count=sold_count,
            total_buy=float(total_buy),
            total_sell=float(total_sell),
            total_profit=float(total_profit),
            average_profit=float(average_profit),
        )
