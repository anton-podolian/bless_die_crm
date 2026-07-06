from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.callback_data import SimpleAction


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✖️ Отмена", callback_data=SimpleAction(action="cancel").pack())]
        ]
    )


def skip_or_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️ Пропустить", callback_data=SimpleAction(action="skip").pack()),
                InlineKeyboardButton(text="✖️ Отмена", callback_data=SimpleAction(action="cancel").pack()),
            ]
        ]
    )


def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖤 В главное меню", callback_data=SimpleAction(action="back_main").pack())]
        ]
    )
