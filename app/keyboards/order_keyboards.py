from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.callback_data import EditField, ListNav, OrderAction, SimpleAction, SizeSelect
from app.models.order import OrderStatus
from app.repositories.order_repository import PAGE_SIZE, SortOption, StatusFilter
from app.utils.formatting import fmt_datetime

SIZES = ["XS", "S", "M", "L", "XL"]

SORT_LABELS = {
    SortOption.NEWEST: "🆕 Сначала новые",
    SortOption.OLDEST: "⏳ Сначала старые",
    SortOption.MOST_EXPENSIVE: "💵 Самые дорогие",
    SortOption.MOST_PROFIT: "💰 Больше прибыль",
}

STATUS_LABELS = {
    StatusFilter.ALL: "🖤 Все",
    StatusFilter.IN_PROGRESS: "🟡 В работе",
    StatusFilter.SOLD: "🟢 Проданные",
}


def size_select_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=size, callback_data=SizeSelect(size=size).pack()) for size in SIZES]
    ]
    rows.append(
        [InlineKeyboardButton(text="✏️ Свой размер", callback_data=SizeSelect(size="CUSTOM").pack())]
    )
    rows.append(
        [InlineKeyboardButton(text="✖️ Отмена", callback_data=SimpleAction(action="cancel").pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_new_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖤 Сохранить заказ", callback_data="new_order:confirm")],
            [InlineKeyboardButton(text="✖️ Отмена", callback_data=SimpleAction(action="cancel").pack())],
        ]
    )


def order_card_kb(order_id: int, status: OrderStatus) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=OrderAction(action="edit", order_id=order_id).pack())],
    ]

    if status == OrderStatus.IN_PROGRESS:
        rows.append(
            [InlineKeyboardButton(text="✅ Закрыть заказ", callback_data=OrderAction(action="close", order_id=order_id).pack())]
        )
    else:
        rows.append(
            [InlineKeyboardButton(text="♻️ Открыть снова", callback_data=OrderAction(action="reopen", order_id=order_id).pack())]
        )

    rows.append(
        [InlineKeyboardButton(text="📋 Дублировать", callback_data=OrderAction(action="duplicate", order_id=order_id).pack())]
    )
    rows.append(
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=OrderAction(action="delete", order_id=order_id).pack())]
    )
    rows.append(
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=SimpleAction(action="back_list").pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def delete_confirm_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Да, удалить",
                    callback_data=OrderAction(action="delete_confirm", order_id=order_id).pack(),
                ),
                InlineKeyboardButton(
                    text="✖️ Отмена",
                    callback_data=OrderAction(action="delete_cancel", order_id=order_id).pack(),
                ),
            ]
        ]
    )


def edit_menu_kb(order_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("🖼 Фото", "photo"),
        ("👕 Название", "title"),
        ("📏 Размер", "size"),
        ("💰 Закупка", "buy_price"),
        ("💵 Продажа", "sell_price"),
        ("👤 Покупатель", "customer"),
        ("📝 Комментарий", "comment"),
        ("🗓 Дата оформления", "created_at"),
    ]
    rows = [
        [InlineKeyboardButton(text=label, callback_data=EditField(order_id=order_id, field=field).pack())]
        for label, field in fields
    ]
    rows.append(
        [InlineKeyboardButton(text="⬅️ Назад к заказу", callback_data=OrderAction(action="view", order_id=order_id).pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def orders_list_kb(
    orders: list,
    total: int,
    page: int,
    status: StatusFilter,
    sort: SortOption,
) -> InlineKeyboardMarkup:
    rows = []

    for order in orders:
        emoji = "🟢" if order.status == OrderStatus.SOLD else "🟡"
        short_title = order.title if len(order.title) <= 24 else f"{order.title[:23]}…"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{emoji} #{order.id} {short_title} · {fmt_datetime(order.created_at)}",
                    callback_data=OrderAction(action="view", order_id=order.id).pack(),
                )
            ]
        )

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=ListNav(page=page - 1, status=status.value, sort=sort.value).pack(),
            )
        )
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data=SimpleAction(action="noop").pack()))
    if page + 1 < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=ListNav(page=page + 1, status=status.value, sort=sort.value).pack(),
            )
        )
    if nav_row:
        rows.append(nav_row)

    status_row = [
        InlineKeyboardButton(
            text=("✅ " if s == status else "") + STATUS_LABELS[s],
            callback_data=ListNav(page=0, status=s.value, sort=sort.value).pack(),
        )
        for s in StatusFilter
    ]
    rows.append(status_row)

    sort_row = [
        InlineKeyboardButton(
            text=("✅ " if s == sort else "") + SORT_LABELS[s],
            callback_data=ListNav(page=0, status=status.value, sort=s.value).pack(),
        )
        for s in SortOption
    ]
    rows.append(sort_row[:2])
    rows.append(sort_row[2:])

    rows.append(
        [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def search_results_kb(orders: list, total: int, page: int, query: str) -> InlineKeyboardMarkup:
    from app.keyboards.callback_data import SearchNav

    rows = []
    for order in orders:
        emoji = "🟢" if order.status == OrderStatus.SOLD else "🟡"
        short_title = order.title if len(order.title) <= 24 else f"{order.title[:23]}…"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{emoji} #{order.id} {short_title} · {fmt_datetime(order.created_at)}",
                    callback_data=OrderAction(action="view", order_id=order.id).pack(),
                )
            ]
        )

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=SearchNav(page=page - 1).pack()))
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data=SimpleAction(action="noop").pack()))
    if page + 1 < total_pages:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=SearchNav(page=page + 1).pack()))
    if nav_row:
        rows.append(nav_row)

    rows.append(
        [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="menu:search")],
    )
    rows.append(
        [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
