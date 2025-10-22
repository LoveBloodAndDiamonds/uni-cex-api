"""Модуль, который предоставляет дополнительные функции, которые могут пригодиться в работе."""

__all__ = [
    "percent_greater",
    "percent_less",
    "TimeoutTracker",
    "generate_ex_link",
    "generate_tv_link",
    "generate_cg_link",
    "make_humanreadable",
    "normalize_ticker",
    "normalize_symbol",
]

import time
from typing import Literal

from .enums import Exchange, MarketType
from .exceptions import NotSupported


def percent_greater(higher: float, lower: float) -> float:
    """Возвращает на сколько процентов `higher` больше `lower`.

    Можно воспринимать полученное значение как если вести линейку на tradingview.com от меньшего значения к большему.

    Например:
        ```python
        percent_greater(120, 100)
        >> 20.0
        ```

    Возвращает:
        `float`: На сколько процентов `higher` больше `lower`.
    """
    if lower == 0:
        return 0.0  # Не будем возвращать float('inf'), чтобы не ломать логику приложения
    return (higher / lower - 1) * 100


def percent_less(higher: float, lower: float) -> float:
    """Возвращает на сколько процентов `lower` меньше `higher`.

    Можно воспринимать полученное значение как если вести линейку на tradingview.com от большего значения к меньшему.

    Например:
        ```python
        percent_less(120, 100)
        >> 16.67777777777777
        ```

    Возвращает:
        `float`: На сколько процентов `lower` меньше `higher`.
    """
    if lower == 0:
        return 0.0  # Не будем возвращать float('inf'), чтобы не ломать логику приложения
    return (1 - lower / higher) * 100


class TimeoutTracker[T]:
    """Универсальный менеджер для управления таймаутами любых объектов.
    Позволяет временно блокировать объекты на заданный промежуток времени.
    """

    def __init__(self) -> None:
        """Инициализирует пустой словарь для отслеживания заблокированных объектов."""
        self._blocked_items: dict[T, float] = {}

    def is_blocked(self, item: T) -> bool:
        """Проверяет, находится ли объект в состоянии блокировки.
        Если срок блокировки истёк, удаляет объект из списка.

        Параметры:
            item (`T`): Объект, который нужно проверить.

        Возвращает:
            `bool`: True, если объект заблокирован, иначе False.
        """
        if item in self._blocked_items:
            if time.time() < self._blocked_items[item]:
                return True
            else:
                del self._blocked_items[item]
        return False

    def block(self, item: T, duration: int) -> None:
        """Блокирует объект на указанное количество секунд.

        Параметры:
            item (`T`): Объект, который нужно заблокировать.
            duration (`int`): Длительность блокировки в секундах.
        """
        self._blocked_items[item] = time.time() + duration


def normalize_ticker(raw_ticker: str) -> str:
    """Нормализует тикер и возвращает базовую валюту (например, `BTC`).

    Эта функция принимает тикер в различных форматах (с разделителями, постфиксом SWAP,
    в верхнем или нижнем регистре) и приводит его к стандартному виду — только базовый актив.

    Примеры:
        ```python
        normalize_ticker("BTC-USDT")  # "BTC"
        normalize_ticker("BTC-USDT-SWAP")  # "BTC"
        normalize_ticker("btc_usdt")  # "BTC"
        normalize_ticker("BTCUSDT")  # "BTC"
        normalize_ticker("BTC")  # "BTC"
        ```

    Параметры:
        raw_ticker (`str`): Исходный тикер в любом из распространённых форматов.

    Возвращает:
        `str`: Базовый актив в верхнем регистре (например, `"BTC"`).
    """
    ticker = raw_ticker.upper()

    # Удаляем постфиксы SWAP
    if ticker.endswith(("SWAP", "-SWAP", "_SWAP", ".SWAP")):
        ticker = (
            ticker.removesuffix("-SWAP")
            .removesuffix("_SWAP")
            .removesuffix(".SWAP")
            .removesuffix("SWAP")
        )

    # Удаляем разделители
    ticker = ticker.translate(str.maketrans("", "", "-_."))

    # Убираем суффикс валюты котировки
    for quote in ("USDT", "USDC"):
        if ticker.endswith(quote):
            ticker = ticker.removesuffix(quote)
            break

    return ticker


def normalize_symbol(raw_ticker: str, quote: Literal["USDT", "USDC"] = "USDT") -> str:
    """Нормализует тикер до унифицированного символа (например, `BTCUSDT`).

    Функция принимает тикер в любом из популярных форматов и возвращает полный символ,
    состоящий из базовой валюты и указанной валюты котировки (`USDT` или `USDC`).

    Примеры:
        ```python
        normalize_symbol("BTC-USDT")  # "BTCUSDT"
        normalize_symbol("BTC")  # "BTCUSDT"
        normalize_symbol("btc_usdt_swap")  # "BTCUSDT"
        normalize_symbol("ETH", "USDC")  # "ETHUSDC"
        ```

    Параметры:
        raw_ticker (`str`): Исходный тикер в любом из распространённых форматов.
        quote (`Literal["USDT", "USDC"]`, optional): Валюта котировки.
            По умолчанию `"USDT"`.

    Возвращает:
        `str`: Символ в унифицированном формате, например `"BTCUSDT"`.
    """
    base = normalize_ticker(raw_ticker)
    return f"{base}{quote}"


def generate_ex_link(exchange: Exchange, market_type: MarketType, symbol: str):
    """Генерирует ссылку на биржу.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка на биржу.
    """
    symbol = normalize_symbol(symbol)
    ticker = normalize_ticker(symbol)
    if exchange == Exchange.BINANCE:
        if market_type == MarketType.FUTURES:
            return f"https://www.binance.com/en/futures/{symbol}"
        else:
            return f"https://www.binance.com/en/trade/{ticker}_USDT?type=spot"
    elif exchange == Exchange.BYBIT:
        if market_type == MarketType.FUTURES:
            return f"https://www.bybit.com/trade/usdt/{symbol}"
        else:
            return f"https://www.bybit.com/en/trade/spot/{ticker}/USDT"
    elif exchange == Exchange.BITGET:
        if market_type == MarketType.FUTURES:
            return f"https://www.bitget.com/ru/futures/usdt/{symbol}"
        else:
            return f"https://www.bitget.com/ru/spot/{symbol}"
    elif exchange == Exchange.OKX:
        if market_type == MarketType.FUTURES:
            return f"https://www.okx.com/ru/trade-swap/{ticker.lower()}-usdt-swap"
        else:
            return f"https://www.okx.com/ru/trade-spot/{ticker.lower()}-usdt"
    elif exchange == Exchange.MEXC:
        if market_type == MarketType.FUTURES:
            return f"https://www.mexc.com/ru-RU/futures/{ticker}_USDT?type=linear_swap"
        else:
            return f"https://www.mexc.com/ru-RU/exchange/{ticker}_USDT"
    elif exchange == Exchange.GATE:
        if market_type == MarketType.FUTURES:
            return f"https://www.gate.com/ru/futures/USDT/{ticker}_USDT"
        else:
            return f"https://www.gate.com/ru/trade/{ticker}_USDT"
    elif exchange == Exchange.XT:
        if market_type == MarketType.FUTURES:
            return f"https://www.xt.com/ru/futures/trade/{ticker.lower()}_usdt"
        else:
            return f"https://www.xt.com/ru/trade/{ticker.lower()}_usdt"
    elif exchange == Exchange.BITUNIX:
        if market_type == MarketType.FUTURES:
            return f"https://www.bitunix.com/ru-ru/contract-trade/{ticker.upper()}USDT"
        else:
            return f"https://www.bitunix.com/ru-ru/spot-trade/{ticker.upper()}USDT"
    elif exchange == Exchange.KCEX:
        if market_type == MarketType.FUTURES:
            return f"https://www.kcex.com/ru-RU/futures/exchange/{ticker.upper()}_USDT"
        else:
            return f"https://www.kcex.com/ru-RU/exchange/{ticker.upper()}_USDT"
    elif exchange == Exchange.HYPERLIQUID:
        if market_type == MarketType.FUTURES:
            return f"https://app.hyperliquid.xyz/trade/{ticker}"
        else:
            return f"https://app.hyperliquid.xyz/trade/{ticker}/USDC"
    else:
        raise NotSupported(f"Exchange {exchange} is not supported")


def generate_tv_link(exchange: Exchange, market_type: MarketType, symbol: str) -> str:
    """Генерирует ссылку для TradingView.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка для TradingView.
    """
    symbol = normalize_symbol(symbol)
    exchange_str = "GATEIO" if exchange == Exchange.GATE else str(exchange)
    if market_type == MarketType.FUTURES:
        return f"https://www.tradingview.com/chart/?symbol={exchange_str}:{symbol}.P"
    else:
        return f"https://www.tradingview.com/chart/?symbol={exchange_str}:{symbol}"


def generate_cg_link(exchange: Exchange, market_type: MarketType, symbol: str) -> str:
    """Генерирует ссылку для CoinGlass.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка для CoinGlass.
    """
    base_url = "https://www.coinglass.com/tv/ru"

    symbol = normalize_symbol(symbol)

    if market_type == MarketType.FUTURES:
        match exchange:
            case Exchange.OKX:
                return f"{base_url}/OKX_{symbol.replace('USDT', '-USDT')}-SWAP"
            case Exchange.MEXC:
                return f"{base_url}/MEXC_{symbol.replace('USDT', '_USDT')}"
            case Exchange.BITGET:
                return f"{base_url}/Bitget_{symbol}_UMCBL"
            case Exchange.GATE:
                return f"{base_url}/Gate_{symbol.replace('USDT', '_USDT')}"
            case Exchange.BITUNIX:
                return f"{base_url}/Bitunix_{symbol}"
            case Exchange.HYPERLIQUID:
                return f"{base_url}/Hyperliquid_{symbol.replace('USDT', '-USD')}"
            case _:
                return f"{base_url}/{exchange.capitalize()}_{symbol}"
    else:
        # Для спота корректная ссылка есть только у OKX
        if exchange == Exchange.OKX:
            return f"{base_url}/SPOT_{exchange.upper()}_{symbol.replace('USDT', '-USDT')}"
        # Для остальных бирж ссылки нет → возвращаем заглушку
        return generate_cg_link(exchange, MarketType.FUTURES, symbol)


def make_humanreadable(value: float, locale: Literal["ru", "en"] = "ru") -> str:
    """Функция превращает большие числа в удобочитаемый вид.

    Принимает:
        value (float): число для преобразования
        locale (Literal["ru", "en"]): язык для форматирования числа

    Возвращает:
        str: Человеческое представление числа
    """
    suffixes = {
        "ru": {
            1_000: "тыс.",
            1_000_000: "млн.",
            1_000_000_000: "млрд.",
            1_000_000_000_000: "трлн.",
            1_000_000_000_000_000: "квдрлн.",
            1_000_000_000_000_000_000: "квнтлн.",
        },
        "en": {
            1_000: "K",
            1_000_000: "M",
            1_000_000_000: "B",
            1_000_000_000_000: "T",
            1_000_000_000_000_000: "Qa",  # Quadrillion
            1_000_000_000_000_000_000: "Qi",  # Quintillion
        },
    }

    selected_suffixes = suffixes[locale]

    for divisor in sorted(selected_suffixes.keys(), reverse=True):
        if abs(value) >= divisor:
            number = value / divisor
            if locale == "ru":
                return (
                    f"{number:,.2f}".replace(",", " ").replace(".", ",")
                    + f" {selected_suffixes[divisor]}"
                )
            return f"{number:,.2f} {selected_suffixes[divisor]}"

    # Форматирование "малых" чисел
    if locale == "ru":
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{value:,.2f}"
