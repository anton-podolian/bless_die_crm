from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.keyboards.callback_data import OrderAction
from app.keyboards.common import cancel_kb
from app.keyboards.order_keyboards import delete_confirm_kb, edit_menu_kb, order_card_kb
from app.models.order import OrderStatus
from app.services.order_service import OrderService
from app.states.order_states import NewOrderStates
from app.utils.formatting import order_card_text
from app.utils.texts import (
    DELETE_CONFIRM,
    ORDER_CLOSED,
    ORDER_DELETED,
    ORDER_DUPLICATED,
    ORDER_REOPENED,
    NEW_ORDER_TITLE,
)

router = Router(name="order_card")

ORDER_NOT_FOUND = "🖤 Заказ не найден. Возможно, он был удалён"


async def _delete_message_if_possible(callback: CallbackQuery) -> bool:
    """Delete the source message, or at least disable its stale keyboard."""
    try:
        await callback.message.delete()
        return True
    except TelegramBadRequest as error:
        if "message can't be deleted" not in error.message.lower():
            raise

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        return False


async def _render_card(callback: CallbackQuery, order) -> None:
    text = order_card_text(order)
    kb = order_card_kb(order.id, order.status, order.is_ordered)

    has_photo_message = bool(callback.message.photo)

    if order.photo_file_id:
        if has_photo_message:
            await callback.message.edit_caption(caption=text, reply_markup=kb)
        else:
            await _delete_message_if_possible(callback)
            await callback.message.answer_photo(order.photo_file_id, caption=text, reply_markup=kb)
    else:
        if has_photo_message:
            await _delete_message_if_possible(callback)
            await callback.message.answer(text, reply_markup=kb)
        else:
            await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(OrderAction.filter(F.action == "view"))
async def view_order(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService, state: FSMContext) -> None:
    await state.set_state(None)
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return
    await _render_card(callback, order)
    await callback.answer()


@router.callback_query(OrderAction.filter(F.action == "close"))
async def close_order(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return
    order = await order_service.close_order(order)
    await _render_card(callback, order)
    await callback.answer(ORDER_CLOSED)


@router.callback_query(OrderAction.filter(F.action == "reopen"))
async def reopen_order(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return
    order = await order_service.reopen_order(order)
    await _render_card(callback, order)
    await callback.answer(ORDER_REOPENED)


@router.callback_query(OrderAction.filter(F.action == "toggle_ordered"))
async def toggle_ordered(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return
    if order.status != OrderStatus.IN_PROGRESS:
        await callback.answer("Статус заказа уже изменился", show_alert=True)
        return
    order = await order_service.toggle_ordered(order)
    await _render_card(callback, order)
    await callback.answer("Вещь заказана" if order.is_ordered else "Вещь не заказана")


@router.callback_query(OrderAction.filter(F.action == "duplicate"))
async def duplicate_order(
    callback: CallbackQuery,
    callback_data: OrderAction,
    order_service: OrderService,
    state: FSMContext,
) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return

    await state.clear()
    await state.update_data(
        photo_file_id=order.photo_file_id,
        size=order.size,
        buy_price=order.buy_price,
        sell_price=order.sell_price,
        customer=None,
        is_duplicate=True,
    )
    await state.set_state(NewOrderStates.title)

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(NEW_ORDER_TITLE, reply_markup=cancel_kb())
    else:
        await callback.message.edit_text(NEW_ORDER_TITLE, reply_markup=cancel_kb())
    await callback.answer(ORDER_DUPLICATED)


@router.callback_query(OrderAction.filter(F.action == "delete"))
async def ask_delete_confirmation(callback: CallbackQuery, callback_data: OrderAction) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(DELETE_CONFIRM, reply_markup=delete_confirm_kb(callback_data.order_id))
    await callback.answer()


@router.callback_query(OrderAction.filter(F.action == "delete_cancel"))
async def cancel_delete(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    await callback.message.delete()
    if order is not None:
        text = order_card_text(order)
        kb = order_card_kb(order.id, order.status, order.is_ordered)
        if order.photo_file_id:
            await callback.message.answer_photo(order.photo_file_id, caption=text, reply_markup=kb)
        else:
            await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(OrderAction.filter(F.action == "delete_confirm"))
async def confirm_delete(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is not None:
        await order_service.delete_order(order)
    await callback.message.delete()
    await callback.message.answer(ORDER_DELETED)
    await callback.answer()


@router.callback_query(OrderAction.filter(F.action == "edit"))
async def open_edit_menu(callback: CallbackQuery, callback_data: OrderAction, order_service: OrderService) -> None:
    order = await order_service.get_order(callback_data.order_id)
    if order is None:
        await callback.answer(ORDER_NOT_FOUND, show_alert=True)
        return

    text = f"✏️ Редактирование заказа #{order.id}\n\nВыбери, что изменить:"
    kb = edit_menu_kb(order.id)

    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
