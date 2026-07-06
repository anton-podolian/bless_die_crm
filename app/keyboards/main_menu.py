from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.callback_data import SimpleAction


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
