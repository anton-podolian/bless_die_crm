from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.callback_data import SearchNav
from app.keyboards.common import cancel_kb
from app.keyboards.order_keyboards import search_results_kb
from app.services.order_service import OrderService
from app.states.order_states import SearchStates
from app.utils.texts import SEARCH_NOTHING_FOUND, SEARCH_PROMPT

router = Router(name="search")


@router.callback_query(F.data == "menu:search")
async def start_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(SearchStates.waiting_query)
    await callback.message.edit_text(SEARCH_PROMPT, reply_markup=cancel_kb())
    await callback.answer()


async def _render_results(message_or_callback, order_service: OrderService, query: str, page: int, state: FSMContext) -> None:
    orders, total = await order_service.search_orders(query=query, page=page)
    await state.update_data(query=query)

    if total == 0:
        text = SEARCH_NOTHING_FOUND
    else:
        text = f"🔍 Результаты по запросу «{query}»\n\nНайдено: {total}"

    kb = search_results_kb(orders, total, page, query)

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=kb)
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=kb)


@router.message(SearchStates.waiting_query)
async def search_query_received(message: Message, state: FSMContext, order_service: OrderService) -> None:
    query = (message.text or "").strip()
    if not query:
        await message.answer(SEARCH_PROMPT, reply_markup=cancel_kb())
        return
    await state.clear()
    await _render_results(message, order_service, query, 0, state)


@router.callback_query(SearchNav.filter())
async def search_page_navigation(callback: CallbackQuery, callback_data: SearchNav, order_service: OrderService, state: FSMContext) -> None:
    data = await state.get_data()
    query = data.get("query", "")
    await _render_results(callback, order_service, query, callback_data.page, state)
