from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.callback_data import SimpleAction, SizeSelect
from app.keyboards.common import cancel_kb, skip_or_cancel_kb
from app.keyboards.main_menu import main_menu_kb
from app.keyboards.order_keyboards import confirm_new_order_kb, order_card_kb, size_select_kb
from app.services.order_service import OrderService
from app.states.order_states import NewOrderStates
from app.utils.formatting import new_order_preview_text, order_card_text
from app.utils.texts import (
    ALL_DONE,
    EMPTY_SIZE,
    EMPTY_TITLE,
    INVALID_PRICE,
    NEW_ORDER_BUY_PRICE,
    NEW_ORDER_COMMENT,
    NEW_ORDER_CUSTOMER,
    NEW_ORDER_SELL_PRICE,
    NEW_ORDER_SIZE,
    NEW_ORDER_SIZE_CUSTOM,
    NEW_ORDER_START,
    NEW_ORDER_TITLE,
    ORDER_SAVED,
)
from app.utils.validators import is_non_empty, parse_price

router = Router(name="new_order")


@router.callback_query(F.data == "menu:new_order")
async def start_new_order(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(NewOrderStates.photo)
    await callback.message.edit_text(NEW_ORDER_START, reply_markup=skip_or_cancel_kb())
    await callback.answer()


@router.message(NewOrderStates.photo, F.photo)
async def photo_received(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=file_id)
    await state.set_state(NewOrderStates.title)
    await message.answer(NEW_ORDER_TITLE, reply_markup=cancel_kb())


@router.message(NewOrderStates.photo)
async def photo_wrong_content(message: Message) -> None:
    await message.answer("🖤 Пришли фото одним изображением или нажми «Пропустить»", reply_markup=skip_or_cancel_kb())


@router.callback_query(NewOrderStates.photo, SimpleAction.filter(F.action == "skip"))
async def photo_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(photo_file_id=None)
    await state.set_state(NewOrderStates.title)
    await callback.message.edit_text(NEW_ORDER_TITLE, reply_markup=cancel_kb())
    await callback.answer()


@router.message(NewOrderStates.title)
async def title_received(message: Message, state: FSMContext) -> None:
    if not is_non_empty(message.text or ""):
        await message.answer(EMPTY_TITLE, reply_markup=cancel_kb())
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(NewOrderStates.size)
    await message.answer(NEW_ORDER_SIZE, reply_markup=size_select_kb())


@router.callback_query(NewOrderStates.size, SizeSelect.filter())
async def size_selected(callback: CallbackQuery, callback_data: SizeSelect, state: FSMContext) -> None:
    if callback_data.size == "CUSTOM":
        await state.set_state(NewOrderStates.size_custom)
        await callback.message.edit_text(NEW_ORDER_SIZE_CUSTOM, reply_markup=cancel_kb())
        await callback.answer()
        return

    await state.update_data(size=callback_data.size)
    await state.set_state(NewOrderStates.buy_price)
    await callback.message.edit_text(NEW_ORDER_BUY_PRICE, reply_markup=cancel_kb())
    await callback.answer()


@router.message(NewOrderStates.size_custom)
async def size_custom_received(message: Message, state: FSMContext) -> None:
    if not is_non_empty(message.text or ""):
        await message.answer(EMPTY_SIZE, reply_markup=cancel_kb())
        return
    await state.update_data(size=message.text.strip())
    await state.set_state(NewOrderStates.buy_price)
    await message.answer(NEW_ORDER_BUY_PRICE, reply_markup=cancel_kb())


@router.message(NewOrderStates.buy_price)
async def buy_price_received(message: Message, state: FSMContext) -> None:
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(INVALID_PRICE, reply_markup=cancel_kb())
        return
    await state.update_data(buy_price=price)
    await state.set_state(NewOrderStates.sell_price)
    await message.answer(NEW_ORDER_SELL_PRICE, reply_markup=cancel_kb())


@router.message(NewOrderStates.sell_price)
async def sell_price_received(message: Message, state: FSMContext) -> None:
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(INVALID_PRICE, reply_markup=cancel_kb())
        return
    await state.update_data(sell_price=price)
    await state.set_state(NewOrderStates.customer)
    await message.answer(NEW_ORDER_CUSTOMER, reply_markup=skip_or_cancel_kb())


@router.message(NewOrderStates.customer)
async def customer_received(message: Message, state: FSMContext) -> None:
    await state.update_data(customer=(message.text or "").strip() or None)
    await _go_to_comment(message, state)


@router.callback_query(NewOrderStates.customer, SimpleAction.filter(F.action == "skip"))
async def customer_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(customer=None)
    await state.set_state(NewOrderStates.comment)
    await callback.message.edit_text(NEW_ORDER_COMMENT, reply_markup=skip_or_cancel_kb())
    await callback.answer()


async def _go_to_comment(message: Message, state: FSMContext) -> None:
    await state.set_state(NewOrderStates.comment)
    await message.answer(NEW_ORDER_COMMENT, reply_markup=skip_or_cancel_kb())


@router.message(NewOrderStates.comment)
async def comment_received(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=(message.text or "").strip() or None)
    await _show_preview(message, state)


@router.callback_query(NewOrderStates.comment, SimpleAction.filter(F.action == "skip"))
async def comment_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(comment=None)
    await _show_preview(callback, state)


async def _show_preview(event, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(NewOrderStates.confirm)
    text = new_order_preview_text(data)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=confirm_new_order_kb())
        await event.answer()
    else:
        await event.answer(text, reply_markup=confirm_new_order_kb())


@router.callback_query(NewOrderStates.confirm, F.data == "new_order:confirm")
async def confirm_new_order(callback: CallbackQuery, state: FSMContext, order_service: OrderService) -> None:
    data = await state.get_data()
    order = await order_service.create_order(data)
    await state.clear()

    text = f"{ORDER_SAVED}\n\n{order_card_text(order)}"
    kb = order_card_kb(order.id, order.status, order.is_ordered)

    if order.photo_file_id:
        await callback.message.delete()
        await callback.message.answer_photo(order.photo_file_id, caption=text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer(ALL_DONE)
