from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.callback_data import EditField
from app.keyboards.common import cancel_kb
from app.keyboards.order_keyboards import order_card_kb
from app.services.order_service import OrderService
from app.states.order_states import EditOrderStates
from app.utils.formatting import order_card_text
from app.utils.texts import EMPTY_SIZE, EMPTY_TITLE, INVALID_PRICE, ORDER_UPDATED
from app.utils.validators import is_non_empty, parse_price

router = Router(name="edit_order")

ORDER_NOT_FOUND = "🖤 Заказ не найден. Возможно, он был удалён"

FIELD_STATE = {
    "photo": EditOrderStates.waiting_photo,
    "title": EditOrderStates.waiting_title,
    "size": EditOrderStates.waiting_size,
    "buy_price": EditOrderStates.waiting_buy_price,
    "sell_price": EditOrderStates.waiting_sell_price,
    "customer": EditOrderStates.waiting_customer,
    "comment": EditOrderStates.waiting_comment,
}

FIELD_PROMPT = {
    "photo": "🖤 Пришли новое фото вещи",
    "title": "🖤 Введи новое название",
    "size": "🖤 Введи новый размер",
    "buy_price": "🖤 Введи новую цену закупки",
    "sell_price": "🖤 Введи новую цену продажи",
    "customer": "🖤 Введи нового покупателя (имя или Instagram)",
    "comment": "🖤 Введи новый комментарий",
}


@router.callback_query(EditField.filter())
async def start_field_edit(callback: CallbackQuery, callback_data: EditField, state: FSMContext) -> None:
    await state.update_data(order_id=callback_data.order_id, field=callback_data.field)
    await state.set_state(FIELD_STATE[callback_data.field])

    prompt = FIELD_PROMPT[callback_data.field]
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(prompt, reply_markup=cancel_kb())
    else:
        await callback.message.edit_text(prompt, reply_markup=cancel_kb())
    await callback.answer()


async def _finish_edit(message: Message, state: FSMContext, order_service: OrderService, order_id: int, field: str, value) -> None:
    order = await order_service.get_order(order_id)
    if order is None:
        await state.clear()
        await message.answer(ORDER_NOT_FOUND)
        return

    order = await order_service.update_field(order, field, value)
    await state.clear()

    text = f"{ORDER_UPDATED}\n\n{order_card_text(order)}"
    kb = order_card_kb(order.id, order.status)

    if order.photo_file_id:
        await message.answer_photo(order.photo_file_id, caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.message(EditOrderStates.waiting_photo, F.photo)
async def edit_photo(message: Message, state: FSMContext, order_service: OrderService) -> None:
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    await _finish_edit(message, state, order_service, data["order_id"], "photo_file_id", file_id)


@router.message(EditOrderStates.waiting_photo)
async def edit_photo_wrong(message: Message) -> None:
    await message.answer("🖤 Пришли изображение одним фото", reply_markup=cancel_kb())


@router.message(EditOrderStates.waiting_title)
async def edit_title(message: Message, state: FSMContext, order_service: OrderService) -> None:
    if not is_non_empty(message.text or ""):
        await message.answer(EMPTY_TITLE, reply_markup=cancel_kb())
        return
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "title", message.text.strip())


@router.message(EditOrderStates.waiting_size)
async def edit_size(message: Message, state: FSMContext, order_service: OrderService) -> None:
    if not is_non_empty(message.text or ""):
        await message.answer(EMPTY_SIZE, reply_markup=cancel_kb())
        return
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "size", message.text.strip())


@router.message(EditOrderStates.waiting_buy_price)
async def edit_buy_price(message: Message, state: FSMContext, order_service: OrderService) -> None:
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(INVALID_PRICE, reply_markup=cancel_kb())
        return
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "buy_price", price)


@router.message(EditOrderStates.waiting_sell_price)
async def edit_sell_price(message: Message, state: FSMContext, order_service: OrderService) -> None:
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(INVALID_PRICE, reply_markup=cancel_kb())
        return
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "sell_price", price)


@router.message(EditOrderStates.waiting_customer)
async def edit_customer(message: Message, state: FSMContext, order_service: OrderService) -> None:
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "customer", (message.text or "").strip() or None)


@router.message(EditOrderStates.waiting_comment)
async def edit_comment(message: Message, state: FSMContext, order_service: OrderService) -> None:
    data = await state.get_data()
    await _finish_edit(message, state, order_service, data["order_id"], "comment", (message.text or "").strip() or None)
