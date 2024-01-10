from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import menu
from db import check_user


async def buy_jetton(call: types.CallbackQuery, state: FSMContext):
    if not check_user(call.from_user.id):
        return
    
    await call.message.answer("Введите адрес жетона для покупки",
                              reply_markup=menu())
    await state.set_state("get_buy_jetton_address")
