from aiogram.fsm.state import State, StatesGroup


class NewOrderStates(StatesGroup):
    photo = State()
    title = State()
    size = State()
    size_custom = State()
    buy_price = State()
    sell_price = State()
    customer = State()
    comment = State()
    confirm = State()


class EditOrderStates(StatesGroup):
    waiting_photo = State()
    waiting_title = State()
    waiting_size = State()
    waiting_buy_price = State()
    waiting_sell_price = State()
    waiting_customer = State()
    waiting_comment = State()
    waiting_created_at = State()


class SearchStates(StatesGroup):
    waiting_query = State()
