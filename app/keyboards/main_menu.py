from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.callback_data import SimpleAction
from app.keyboards.callback_data import StatsMonth


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Новый заказ", callback_data="menu:new_order")],
            [InlineKeyboardButton(text="📦 Все заказы", callback_data="menu:orders")],
            [InlineKeyboardButton(text="🔍 Поиск", callback_data="menu:search")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="menu:stats")],
            [InlineKeyboardButton(text="🕐 Последний заказ", callback_data="menu:last_order")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())]
        ]
    )


def stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Статистика по месяцам", callback_data="stats:monthly")],
            [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())],
        ]
    )


def month_stats_kb(year: int, month: int) -> InlineKeyboardMarkup:
    previous_year, previous_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Предыдущий",
                    callback_data=StatsMonth(year=previous_year, month=previous_month).pack(),
                ),
                InlineKeyboardButton(
                    text="Следующий ➡️",
                    callback_data=StatsMonth(year=next_year, month=next_month).pack(),
                ),
            ],
            [InlineKeyboardButton(text="📊 Общая статистика", callback_data="menu:stats")],
            [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())],
        ]
    )
