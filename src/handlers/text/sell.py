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
from dedust import Asset, Factory, PoolType, JettonRoot, VaultJetton, SwapStep

async def get_sell_jetton_address(message: types.Message, state: FSMContext):
    await state.update_data(jetton_address=message.text)
    await message.answer("Введите адрес роутинг жетона(0 - если без роутинг адреса)",
                         reply_markup=menu())
    await state.set_state("get_sell_routing_address")

async def get_sell_routing_address(message: types.Message, state: FSMContext):
    await state.update_data(routing_address=message.text)
    await message.answer("Введите сумму обмена(в JETTON)",
                         reply_markup=menu())
    await state.set_state("get_jetton_swap_amount")

async def get_jetton_swap_amount(message: types.Message, state: FSMContext):
    await state.update_data(swap_amount=float(message.text))
    await message.answer("Введите decimals жетона для продажи",
                         reply_markup=menu())
    await state.set_state("get_jetton_decimals")

async def get_jetton_decimals(message: types.Message, state: FSMContext):
    try:
        storage = FileStorage(f"connections/{message.from_user.id}.json")
        connector = TonConnect(CONNECT_URL, storage)

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

        JETTON = Asset.jetton(data["jetton_address"])
        TON = Asset.native()

        _next = None
        provider = LiteBalancer.from_config(config=network_config)
        try:
            await provider.start_up()

            jetton_vault = await Factory.get_jetton_vault(data["jetton_address"], provider)
            jetton_root = JettonRoot.create_from_address(data["jetton_address"])
            jetton_wallet = await jetton_root.get_wallet(user_address, provider)

            if data["routing_address"] != "0":
                # JETTON_ADDRESS -> ROUTING_ADDRESS -> TON
                pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                            assets=[JETTON, Asset.jetton(data["routing_address"])],
                                            provider=provider)
                routing_pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                                    assets=[Asset.jetton(data["routing_address"]), TON],
                                                    provider=provider)
                _next = SwapStep(pool_address=routing_pool.address)
            else:
                # JETTON_ADDRESS -> TON
                pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                            assets=[JETTON, TON],
                                            provider=provider)
            await provider.close_all()
        except:
            await message.answer("Ошибка провайдера! Попробуйте позже",
                                  reply_markup=menu())
            await state.finish()
            await provider.close_all()
            return

        swap_body = jetton_wallet.create_transfer_payload(destination=jetton_vault.address,
                                                        amount=int(data["swap_amount"] * 10 ** float(message.text)),
                                                        response_address=user_address,
                                                        forward_amount=int(0.25*1e9),
                                                        forward_payload=VaultJetton.create_swap_payload(pool_address=pool.address,
                                                                                                        _next=_next))

        transaction["messages"].append(
            {
                "address": jetton_wallet.address.to_str(),
                "amount": str(int(0.3*1e9)),
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
