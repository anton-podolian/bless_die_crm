from aiogram import Router

from app.handlers import edit_order, new_order, order_card, orders_list, search, start

router = Router(name="root")

router.include_router(start.router)
router.include_router(new_order.router)
router.include_router(order_card.router)
router.include_router(edit_order.router)
router.include_router(orders_list.router)
router.include_router(search.router)
