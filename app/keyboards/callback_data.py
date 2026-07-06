from aiogram.filters.callback_data import CallbackData


class OrderAction(CallbackData, prefix="ord"):
    action: str  # view | edit | close | reopen | delete | delete_confirm | delete_cancel | duplicate
    order_id: int


class EditField(CallbackData, prefix="edf"):
    order_id: int
    field: str  # photo | title | size | buy_price | sell_price | customer | comment


class SizeSelect(CallbackData, prefix="sz"):
    size: str  # XS | S | M | L | XL | CUSTOM


class ListNav(CallbackData, prefix="lst"):
    page: int
    status: str
    sort: str


class ListStatusSelect(CallbackData, prefix="lsts"):
    status: str
    sort: str


class ListSortSelect(CallbackData, prefix="lstsrt"):
    status: str
    sort: str


class SearchNav(CallbackData, prefix="srch"):
    page: int


class SimpleAction(CallbackData, prefix="act"):
    action: str  # cancel | skip | back_main | back_list | noop
