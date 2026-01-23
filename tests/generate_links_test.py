from unicex.extra import (
    normalize_ticker,
    normalize_symbol,
    generate_tv_link,
    generate_ex_link,
    generate_cg_link,
)
from unicex import MarketType, Exchange


def test_normalize_functions():
    print("🧪 Тестируем normalize_ticker() и normalize_symbol()...")

    # --- normalize_ticker() ---
    assert normalize_ticker("BTC-USDT") == "BTC"
    assert normalize_ticker("BTC-USDT-SWAP") == "BTC"
    assert normalize_ticker("BTC_USDT_SWAP") == "BTC"
    assert normalize_ticker("BTC.USDT") == "BTC"
    assert normalize_ticker("BTCUSDT") == "BTC"
    assert normalize_ticker("BTC") == "BTC"
    assert normalize_ticker("btc") == "BTC"
    assert normalize_ticker("btc_usdt") == "BTC"
    assert normalize_ticker("BTC-USDC") == "BTC"
    assert normalize_ticker("BTCUSDC") == "BTC"
    assert normalize_ticker("ETH-USDT") == "ETH"
    assert normalize_ticker("ETHUSDC") == "ETH"
    assert normalize_ticker("SOL") == "SOL"
    assert normalize_ticker("SOL_SWAP") == "SOL"

    # --- normalize_symbol() ---
    assert normalize_symbol("BTC-USDT") == "BTCUSDT"
    assert normalize_symbol("BTC-USDT-SWAP") == "BTCUSDT"
    assert normalize_symbol("BTC_USDT_SWAP") == "BTCUSDT"
    assert normalize_symbol("BTC") == "BTCUSDT"
    assert normalize_symbol("btc_usdt") == "BTCUSDT"
    assert normalize_symbol("btc") == "BTCUSDT"
    assert normalize_symbol("BTC", "USDC") == "BTCUSDC"
    assert normalize_symbol("BTCUSDT", "USDC") == "BTCUSDC"  # переопределение quote
    assert normalize_symbol("BTCUSDC", "USDT") == "BTCUSDT"
    assert normalize_symbol("ETH-USDC") == "ETHUSDT"
    assert normalize_symbol("eth", "USDC") == "ETHUSDC"
    assert normalize_symbol("SOL_SWAP") == "SOLUSDT"
    assert normalize_symbol("SOL_SWAP", "USDC") == "SOLUSDC"
    assert normalize_symbol("doge_usdt_swap") == "DOGEUSDT"
    assert normalize_symbol("xrp") == "XRPUSDT"

    print("✅ Все тесты успешно пройдены!")

    print("=" * 80)


def test_generate_links():
    """Проверяет генерацию ссылок для всех бирж и типов рынка."""
    symbol = "ETHUSDT"

    print("🧪 Тестирование генерации ссылок...")

    for exchange in Exchange:
        for market_type in MarketType:
            print(f"\n🌐 {exchange.name} | {market_type.name}")
            print("-" * 80)

            try:
                ex_link = generate_ex_link(exchange, market_type, symbol)
            except Exception as e:
                ex_link = f"⚠️ Ошибка: {e}"

            try:
                tv_link = generate_tv_link(exchange, market_type, symbol)
            except Exception as e:
                tv_link = f"⚠️ Ошибка: {e}"

            try:
                cg_link = generate_cg_link(exchange, market_type, symbol)
            except Exception as e:
                cg_link = f"⚠️ Ошибка: {e}"

            print(f"📈 Exchange:     {ex_link}")
            print(f"📊 TradingView:  {tv_link}")
            print(f"🧠 CoinGlass:    {cg_link}")
            print("-" * 80)

    print("\n✅ Тестирование ссылок завершено!")
    print("=" * 80)


# Запуск тестов
if __name__ == "__main__":
    test_normalize_functions()
    test_generate_links()
