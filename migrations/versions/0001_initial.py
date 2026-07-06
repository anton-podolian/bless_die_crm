"""initial

Revision ID: 0001
Revises:
Create Date: 2026-07-06 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("photo_file_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("size", sa.String(length=50), nullable=False),
        sa.Column("buy_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("sell_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("profit", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("customer", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_title", "orders", ["title"])
    op.create_index("ix_orders_customer", "orders", ["customer"])


def downgrade() -> None:
    op.drop_index("ix_orders_customer", table_name="orders")
    op.drop_index("ix_orders_title", table_name="orders")
    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
