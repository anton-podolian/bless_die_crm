from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.keyboards.callback_data import ListNav, SimpleAction
from app.keyboards.order_keyboards import SORT_LABELS, STATUS_LABELS, orders_list_kb
from app.repositories.order_repository import SortOption, StatusFilter
from app.services.order_service import OrderService
from app.utils.formatting import order_list_header
from app.utils.texts import NO_ORDERS_YET

router = Router(name="orders_list")


async def _render_list(callback: CallbackQuery, order_service: OrderService, page: int, status: StatusFilter, sort: SortOption) -> None:
    orders, total = await order_service.list_orders(page=page, status_filter=status, sort=sort)

    if total == 0:
        await callback.message.edit_text(NO_ORDERS_YET, reply_markup=orders_list_kb([], 0, 0, status, sort))
        return

    header = order_list_header(STATUS_LABELS[status], SORT_LABELS[sort], total)
    kb = orders_list_kb(orders, total, page, status, sort)
    await callback.message.edit_text(header, reply_markup=kb)


@router.callback_query(F.data == "menu:orders")
async def open_orders_list(callback: CallbackQuery, order_service: OrderService, state: FSMContext) -> None:
    await state.clear()
    page = 0
    status = StatusFilter.ALL
    sort = SortOption.NEWEST
    await state.update_data(list_page=page, list_status=status.value, list_sort=sort.value)
    await _render_list(callback, order_service, page=page, status=status, sort=sort)
    await callback.answer()


@router.callback_query(SimpleAction.filter(F.action == "back_list"))
async def back_to_orders_list(callback: CallbackQuery, order_service: OrderService, state: FSMContext) -> None:
    data = await state.get_data()
    page = data.get("list_page", 0)
    try:
        status = StatusFilter(data.get("list_status", StatusFilter.ALL.value))
        sort = SortOption(data.get("list_sort", SortOption.NEWEST.value))
    except ValueError:
        page = 0
        status = StatusFilter.ALL
        sort = SortOption.NEWEST

    await state.clear()
    await state.update_data(list_page=page, list_status=status.value, list_sort=sort.value)
    if callback.message.photo:
        await callback.message.delete()
        orders, total = await order_service.list_orders(page=page, status_filter=status, sort=sort)
        if total == 0:
            await callback.message.answer(NO_ORDERS_YET, reply_markup=orders_list_kb([], 0, 0, status, sort))
        else:
            header = order_list_header(STATUS_LABELS[status], SORT_LABELS[sort], total)
            kb = orders_list_kb(orders, total, page, status, sort)
            await callback.message.answer(header, reply_markup=kb)
    else:
        await _render_list(callback, order_service, page=page, status=status, sort=sort)
    await callback.answer()


@router.callback_query(ListNav.filter())
async def navigate_orders_list(
    callback: CallbackQuery, callback_data: ListNav, order_service: OrderService, state: FSMContext
) -> None:
    status = StatusFilter(callback_data.status)
    sort = SortOption(callback_data.sort)
    await state.update_data(list_page=callback_data.page, list_status=status.value, list_sort=sort.value)
    await _render_list(callback, order_service, page=callback_data.page, status=status, sort=sort)
    await callback.answer()
