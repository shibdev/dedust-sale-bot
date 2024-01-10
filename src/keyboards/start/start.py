from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="Меню", callback_data="menu"))
                                     
def start_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text="🟢 Купить жетон", callback_data="buy_jetton"),
               InlineKeyboardButton(text="🔴 Продать жетон", callback_data="sell_jetton"),
               InlineKeyboardButton(text="❌ Отключить кошелёк", callback_data="disconnect")]

    keyboard.add(*buttons)

    return keyboard

def connect_buttons():
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="Tonkeeper", callback_data="tonkeeper_button")).add(InlineKeyboardButton(text="TonHub", callback_data="tonhub_button"))
