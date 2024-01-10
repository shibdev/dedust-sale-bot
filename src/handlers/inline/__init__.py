from aiogram import Dispatcher
from handlers.inline.start import disconnect, tonkeeper_connect, tonhub_connect
from handlers.inline.buy import buy_jetton
from handlers.inline.sell import sell_jetton
from handlers.inline.menu import menu


def register_inline_handler(dp: Dispatcher):
    dp.register_callback_query_handler(disconnect, text="disconnect")

    dp.register_callback_query_handler(buy_jetton, text="buy_jetton")
    dp.register_callback_query_handler(sell_jetton, text="sell_jetton")

    dp.register_callback_query_handler(menu, text="menu", state="*")

    dp.register_callback_query_handler(tonkeeper_connect, lambda c: c.data.startswith("tonkeeper_button"))
    dp.register_callback_query_handler(tonhub_connect, lambda c: c.data.startswith("tonhub_button"))
  