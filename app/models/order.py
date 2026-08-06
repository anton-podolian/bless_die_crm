from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, Text, event, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class OrderStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SOLD = "sold"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    photo_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[str] = mapped_column(String(50), nullable=False)

    buy_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sell_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    profit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    customer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status", native_enum=False, length=20),
        default=OrderStatus.IN_PROGRESS,
        nullable=False,
    )
    is_ordered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Order #{self.id} {self.title!r} status={self.status}>"


def _recalculate_profit(mapper, connection, target: Order) -> None:
    """Profit is always derived from buy/sell price - never set manually."""
    buy = float(target.buy_price or 0)
    sell = float(target.sell_price or 0)
    target.profit = sell - buy


event.listen(Order, "before_insert", _recalculate_profit)
event.listen(Order, "before_update", _recalculate_profit)
