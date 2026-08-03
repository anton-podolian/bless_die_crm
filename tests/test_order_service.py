import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

from app.models.order import OrderStatus
from app.services.order_service import OrderService
from app.utils.formatting import fmt_datetime


class FakeRepository:
    def __init__(self):
        self.orders = {}
        self.period = None

    async def update(self, order, **fields):
        for key, value in fields.items():
            setattr(order, key, value)
        self.orders[order.id] = order
        return order

    async def get_by_id(self, order_id):
        return self.orders.get(order_id)

    async def get_stats_for_period(self, start, end):
        self.period = (start, end)
        return SimpleNamespace(total_count=0)


def test_closed_order_remains_saved_and_can_be_loaded():
    async def scenario():
        repository = FakeRepository()
        order = SimpleNamespace(id=42, status=OrderStatus.IN_PROGRESS, closed_at=None)
        repository.orders[order.id] = order
        service = OrderService(repository)

        await service.close_order(order)
        saved = await service.get_order(order.id)

        assert saved is order
        assert saved.status == OrderStatus.SOLD
        assert saved.closed_at is not None

    asyncio.run(scenario())


def test_reopening_does_not_change_original_order_date():
    async def scenario():
        repository = FakeRepository()
        created_at = datetime(2025, 5, 10, 8, 0, tzinfo=UTC)
        order = SimpleNamespace(
            id=7,
            status=OrderStatus.SOLD,
            created_at=created_at,
            closed_at=datetime(2025, 5, 11, 8, 0, tzinfo=UTC),
        )
        repository.orders[order.id] = order

        reopened = await OrderService(repository).reopen_order(order)

        assert reopened.status == OrderStatus.IN_PROGRESS
        assert reopened.closed_at is None
        assert reopened.created_at == created_at

    asyncio.run(scenario())


def test_month_boundaries_follow_kyiv_timezone_and_dst():
    async def scenario():
        repository = FakeRepository()
        await OrderService(repository).get_month_stats(2026, 4)
        start, end = repository.period

        assert start == datetime(2026, 3, 31, 21, 0, tzinfo=UTC)
        assert end == datetime(2026, 4, 30, 21, 0, tzinfo=UTC)

    asyncio.run(scenario())


def test_order_time_is_rendered_in_kyiv():
    assert fmt_datetime(datetime(2026, 1, 15, 10, 30, tzinfo=UTC)) == "15.01.2026 12:30"
    assert fmt_datetime(datetime(2026, 7, 15, 10, 30, tzinfo=UTC)) == "15.07.2026 13:30"
