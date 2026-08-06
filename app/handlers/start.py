from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.callback_data import SimpleAction, StatsMonth
from app.keyboards.main_menu import main_menu_kb, month_stats_kb, settings_kb, stats_kb
from app.services.order_service import OrderService
from app.utils.formatting import order_card_text
from app.utils.texts import (
    ACTION_CANCELED,
    NO_LAST_ORDER,
    SETTINGS_TEXT,
    WELCOME,
)

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu_kb())


async def show_main_menu(callback_or_message, state: FSMContext) -> None:
    await state.clear()
    text = WELCOME
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.edit_text(text, reply_markup=main_menu_kb())
        await callback_or_message.answer()
    else:
        await callback_or_message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(SimpleAction.filter(F.action == "back_main"))
async def cb_back_main(callback: CallbackQuery, state: FSMContext) -> None:
    await show_main_menu(callback, state)


@router.callback_query(SimpleAction.filter(F.action == "cancel"))
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(f"{ACTION_CANCELED}\n\n{WELCOME}", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(SimpleAction.filter(F.action == "noop"))
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "menu:stats")
async def cb_stats(callback: CallbackQuery, order_service: OrderService) -> None:
    from app.utils.formatting import stats_text

    stats = await order_service.get_stats()
    await callback.message.edit_text(stats_text(stats), reply_markup=stats_kb())
    await callback.answer()


MONTH_NAMES = (
    "", "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
)


async def _show_month_stats(
    callback: CallbackQuery, order_service: OrderService, year: int, month: int
) -> None:
    from app.utils.formatting import stats_text

    stats = await order_service.get_month_stats(year, month)
    period = f"{MONTH_NAMES[month]} {year}"
    await callback.message.edit_text(
        stats_text(stats, period=period), reply_markup=month_stats_kb(year, month)
    )


@router.callback_query(F.data == "stats:monthly")
async def cb_monthly_stats(callback: CallbackQuery, order_service: OrderService) -> None:
    now = datetime.now(ZoneInfo("Europe/Kyiv"))
    await _show_month_stats(callback, order_service, now.year, now.month)
    await callback.answer()


@router.callback_query(StatsMonth.filter())
async def cb_month_stats_nav(
    callback: CallbackQuery, callback_data: StatsMonth, order_service: OrderService
) -> None:
    await _show_month_stats(callback, order_service, callback_data.year, callback_data.month)
    await callback.answer()


@router.callback_query(F.data == "menu:last_order")
async def cb_last_order(callback: CallbackQuery, order_service: OrderService) -> None:
    from app.keyboards.order_keyboards import order_card_kb

    order = await order_service.get_last_order()
    if order is None:
        await callback.message.edit_text(NO_LAST_ORDER, reply_markup=settings_kb())
        await callback.answer()
        return

    text = order_card_text(order)
    kb = order_card_kb(order.id, order.status, order.is_ordered)

    if order.photo_file_id:
        await callback.message.delete()
        await callback.message.answer_photo(order.photo_file_id, caption=text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def cb_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(SETTINGS_TEXT, reply_markup=settings_kb())
    await callback.answer()


@router.message(StateFilter(None))
async def fallback_message(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_menu_kb())
