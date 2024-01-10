from aiogram import Dispatcher
from handlers.text.start import start
from handlers.text.buy import get_buy_jetton_address, get_buy_routing_address, get_ton_swap_amount
from handlers.text.sell import get_sell_jetton_address, get_sell_routing_address, get_jetton_swap_amount, get_jetton_decimals

def register_text_handler(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])

    # Buy
    dp.register_message_handler(get_buy_jetton_address, state="get_buy_jetton_address")
    dp.register_message_handler(get_buy_routing_address, state="get_buy_routing_address")
    dp.register_message_handler(get_ton_swap_amount, state="get_ton_swap_amount")

    # Sell
    dp.register_message_handler(get_sell_jetton_address, state="get_sell_jetton_address")
    dp.register_message_handler(get_sell_routing_address, state="get_sell_routing_address")
    dp.register_message_handler(get_jetton_swap_amount, state="get_jetton_swap_amount")
    dp.register_message_handler(get_jetton_decimals, state="get_jetton_decimals")
