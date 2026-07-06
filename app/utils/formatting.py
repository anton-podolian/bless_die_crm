from __future__ import annotations

from app.models.order import Order, OrderStatus
from app.repositories.order_repository import OrderStats

STATUS_TEXT = {
    OrderStatus.IN_PROGRESS: "🟡 В работе",
    OrderStatus.SOLD: "🟢 Продан",
}


def fmt_money(value: float) -> str:
    value = float(value)
    if value == int(value):
        return f"{int(value)}$"
    return f"{value:.2f}$"


def fmt_datetime(dt) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def profit_emoji(profit: float) -> str:
    if profit > 0:
        return "📈"
    if profit < 0:
        return "📉"
    return "➖"


def order_card_text(order: Order) -> str:
    lines = [f"🖤 Заказ #{order.id}", ""]

    lines.append(f"👕 {order.title}")
    lines.append(f"📏 Размер: {order.size}")
    lines.append("")
    lines.append(f"💰 Закупка: {fmt_money(order.buy_price)}")
    lines.append(f"💵 Продажа: {fmt_money(order.sell_price)}")
    lines.append(f"{profit_emoji(float(order.profit))} Прибыль: {fmt_money(order.profit)}")
    lines.append("")
    lines.append(f"👤 Покупатель: {order.customer or '—'}")

    if order.comment:
        lines.append(f"📝 {order.comment}")

    lines.append("")
    lines.append(f"Статус: {STATUS_TEXT[order.status]}")
    lines.append("")
    lines.append(f"🗓 Создан: {fmt_datetime(order.created_at)}")

    if order.closed_at:
        lines.append(f"✅ Продан: {fmt_datetime(order.closed_at)}")

    lines.append(f"🔄 Обновлён: {fmt_datetime(order.updated_at)}")

    return "\n".join(lines)


def order_list_header(status_label: str, sort_label: str, total: int) -> str:
    return (
        f"📦 Все заказы\n\n"
        f"Фильтр: {status_label}\n"
        f"Сортировка: {sort_label}\n"
        f"Найдено: {total}\n"
    )


def stats_text(stats: OrderStats) -> str:
    return (
        "📊 Статистика\n\n"
        f"🧾 Всего заказов: {stats.total_count}\n"
        f"🟡 В работе: {stats.in_progress_count}\n"
        f"🟢 Продано: {stats.sold_count}\n\n"
        f"💰 Общая сумма закупок: {fmt_money(stats.total_buy)}\n"
        f"💵 Общая сумма продаж: {fmt_money(stats.total_sell)}\n"
        f"{profit_emoji(stats.total_profit)} Общая прибыль: {fmt_money(stats.total_profit)}\n"
        f"📐 Средняя прибыль: {fmt_money(stats.average_profit)}"
    )


def new_order_preview_text(data: dict) -> str:
    lines = ["🖤 Проверь заказ перед сохранением", ""]
    lines.append(f"👕 {data.get('title')}")
    lines.append(f"📏 Размер: {data.get('size')}")
    lines.append(f"💰 Закупка: {fmt_money(data.get('buy_price', 0))}")
    lines.append(f"💵 Продажа: {fmt_money(data.get('sell_price', 0))}")
    profit = float(data.get("sell_price", 0)) - float(data.get("buy_price", 0))
    lines.append(f"{profit_emoji(profit)} Прибыль: {fmt_money(profit)}")
    lines.append(f"👤 Покупатель: {data.get('customer') or '—'}")
    if data.get("comment"):
        lines.append(f"📝 {data.get('comment')}")
    return "\n".join(lines)
