from aiogram import types
from aiogram.dispatcher import FSMContext
from pytonconnect import TonConnect
from pytonconnect.storage import FileStorage
from pytoniq import LiteBalancer
from keyboards import menu
from db import get_user_address
from config import CONNECT_URL, network_config
import time
from tonsdk.utils import bytes_to_b64str
from dedust import Asset, Factory, PoolType, SwapParams, VaultNative, SwapStep

async def get_buy_jetton_address(message: types.Message, state: FSMContext):
    await state.update_data(jetton_address=message.text)
    await message.answer("Введите адрес роутинг жетона(0 - если без роутинг адреса)",
                         reply_markup=menu())
    await state.set_state("get_buy_routing_address")

async def get_buy_routing_address(message: types.Message, state: FSMContext):
    await state.update_data(routing_address=message.text)
    await message.answer("Введите сумму обмена(в TON)",
                         reply_markup=menu())
    await state.set_state("get_ton_swap_amount")

async def get_ton_swap_amount(message: types.Message, state: FSMContext):
    storage = FileStorage(f"connections/{message.from_user.id}.json")
    connector = TonConnect(CONNECT_URL, storage)

    try:
        is_connected = await connector.restore_connection()
        if not is_connected:
            print("Not connected")
            return

        transaction = {
            "valid_until": (int(time.time()) + 900) * 1000,
            "messages": []
        }

        user_address = get_user_address(message.from_user.id)
        data = await state.get_data()

        TON = Asset.native()
        JETTON = Asset.jetton(data["jetton_address"])

        swap_params = SwapParams(deadline=int(time.time() + 900 * 5),
                                recipient_address=user_address)
        _next = None
        provider = LiteBalancer.from_config(config=network_config)
        try:
            await provider.start_up()

            if data["routing_address"] != "0":
                # TON -> ROUTING_ADDRESS -> JETTON_ADDRESS
                pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                            assets=[TON, Asset.jetton(data["routing_address"])],
                                            provider=provider)
                routing_pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                            assets=[Asset.jetton(data["routing_address"]), JETTON],
                                            provider=provider)
                _next = SwapStep(pool_address=routing_pool.address)
            else:
                # TON -> JETTON_ADDRESS
                pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                            assets=[TON, JETTON],
                                            provider=provider)
            await provider.close_all()
        except:
            await message.answer("Ошибка провайдера! Попробуйте позже",
                                  reply_markup=menu())
            await state.finish()
            await provider.close_all()
            return
        swap_body = VaultNative.create_swap_payload(amount=int(float(message.text) * 1e9),
                                                    pool_address=pool.address,
                                                    swap_params=swap_params,
                                                    _next=_next)

        transaction["messages"].append(
            {
                "address": "EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_",
                "amount": str(int((float(message.text) + 0.25)*1e9)),
                "payload": bytes_to_b64str(swap_body.to_boc(False))
            }
        )

        await message.answer("Теперь подтверди транзакцию")

        await connector.send_transaction(transaction)
        await message.answer("Успех!",
                                reply_markup=menu())

    except Exception as e:
        await message.answer(f"Ошибка: {e}",
                                reply_markup=menu())
    
    await state.finish()
