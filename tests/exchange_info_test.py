import asyncio
from unicex import start_exchanges_info, get_exchange_info, Exchange


async def main() -> None:
    # ⏳ Запускаем фоновые процессы, которые собирают рыночные параметры всех бирж:
    #  - количество знаков после точки для цены и объема
    #  - множители контрактов для фьючерсов
    await start_exchanges_info()

    # Небольшая пауза, чтобы данные успели подгрузиться
    await asyncio.sleep(1)

    # 1️⃣ Пример 1: Округление цены для фьючерсов OKX
    okx_exchange_info = get_exchange_info(Exchange.OKX)
    okx_rounded_price = okx_exchange_info.round_futures_price("BTC-USDT-SWAP", 123456.1234567890)
    print(okx_rounded_price)  # >> 123456.1

    # 2️⃣ Пример 2: Округление объема для спота Binance
    binance_exchange_info = get_exchange_info(Exchange.BINANCE)
    binance_rounded_quantity = binance_exchange_info.round_quantity("BTCUSDT", 1.123456789)
    print(binance_rounded_quantity)  # >> 1.12345

    # 3️⃣ Пример 3: Получение множителя контракта (например, Mexc Futures)
    mexc_exchange_info = get_exchange_info(Exchange.MEXC)
    mexc_contract_multiplier = mexc_exchange_info.get_futures_ticker_info("BTC_USDT")[
        "contract_size"
    ]
    print(mexc_contract_multiplier)  # >> 0.0001

    # 4️⃣ Пример 4: Реальное применение — вычисляем тейк-профит вручную
    # Допустим, позиция открыта по 123123.1 USDT, хотим +3.5% тейк-профит:
    take_profit_raw = 123123.1 * 1.035
    print("До округления:", take_profit_raw)  # >> 127432.40849999999

    # Биржа требует цену в допустимом формате — округляем:
    take_profit = okx_exchange_info.round_futures_price("BTC-USDT-SWAP", take_profit_raw)
    print("После округления:", take_profit)  # >> 127432.4

    # Теперь это число можно безопасно передать в API без ошибок:
    # await client.create_order(symbol="BTC-USDT-SWAP", price=take_profit, ...)


if __name__ == "__main__":
    asyncio.run(main())
