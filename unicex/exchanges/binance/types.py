from typing import Literal

type SpotTimeframe = Literal[
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]
"""Возможные интервалы для запросов исторических данных на споте."""

type FuturesTimeframe = Literal[
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]
"""Возможные интервалы для запросов исторических данных на фьючерсах."""

type Side = Literal["BUY", "SELL"]
"""Возможные стороны для торговли."""

type OrderType = Literal[
    "LIMIT",
    "MARKET",
    "STOP_LOSS",
    "STOP_LOSS_LIMIT",
    "TAKE_PROFIT",
    "TAKE_PROFIT_LIMIT",
    "LIMIT_MAKER",
]
"""Возможные типы ордеров."""

type NewOrderRespType = Literal["ACK", "RESULT", "FULL"]
"""Возможные типы ответов на запросы создания ордеров."""

type TimeInForce = Literal["GTC", "IOC", "FOK"]
"""Возможные типы действия ордера."""

type SelfTradePreventionMode = Literal["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"]
"""Возможные режимы предотвращения самообмена."""

type TickerType = Literal["FULL", "MINI"]
"""Возможные типы тикера для статистики."""

type WindowSize = Literal[
    "1m",
    "2m",
    "3m",
    "4m",
    "5m",
    "6m",
    "7m",
    "8m",
    "9m",
    "10m",
    "11m",
    "12m",
    "13m",
    "14m",
    "15m",
    "16m",
    "17m",
    "18m",
    "19m",
    "20m",
    "21m",
    "22m",
    "23m",
    "24m",
    "25m",
    "26m",
    "27m",
    "28m",
    "29m",
    "30m",
    "31m",
    "32m",
    "33m",
    "34m",
    "35m",
    "36m",
    "37m",
    "38m",
    "39m",
    "40m",
    "41m",
    "42m",
    "43m",
    "44m",
    "45m",
    "46m",
    "47m",
    "48m",
    "49m",
    "50m",
    "51m",
    "52m",
    "53m",
    "54m",
    "55m",
    "56m",
    "57m",
    "58m",
    "59m",
    "1h",
    "2h",
    "3h",
    "4h",
    "5h",
    "6h",
    "7h",
    "8h",
    "9h",
    "10h",
    "11h",
    "12h",
    "13h",
    "14h",
    "15h",
    "16h",
    "17h",
    "18h",
    "19h",
    "20h",
    "21h",
    "22h",
    "23h",
    "1d",
    "2d",
    "3d",
    "4d",
    "5d",
    "6d",
    "7d",
]
"""Возможные размеры окон для скользящей статистики."""

type StatsPeriod = Literal["5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
"""Возможные периоды для статистики по открытому интересу."""

type RatioType = Literal[
    "topLongShortAccountRatio", "topLongShortPositionRatio", "globalLongShortAccountRatio"
]
"""Возможные типы статистики лонг/шорт позиций."""

type FuturesOrderType = Literal[
    "LIMIT",
    "MARKET",
    "STOP",
    "STOP_MARKET",
    "TAKE_PROFIT",
    "TAKE_PROFIT_MARKET",
    "TRAILING_STOP_MARKET",
]
"""Возможные типы ордеров на фьючерсах."""

type FuturesTimeInForce = Literal["GTC", "IOC", "FOK", "GTX"]
"""Возможные типы действия ордера на фьючерсах."""

type WorkingType = Literal["MARK_PRICE", "CONTRACT_PRICE"]
"""Возможные типы цены для стоп-ордеров на фьючерсах."""

type PositionSide = Literal["BOTH", "LONG", "SHORT"]
"""Возможные стороны позиции на фьючерсах."""

type OrderStatus = Literal[
    "NEW",
    "PARTIALLY_FILLED",
    "FILLED",
    "CANCELED",
    "PENDING_CANCEL",
    "REJECTED",
    "EXPIRED",
    "EXPIRED_IN_MATCH",
]
"""Возможные статусы ордеров."""

type ContingencyType = Literal["OCO"]
"""Возможные типы контингентных ордеров."""

type ListStatusType = Literal["RESPONSE", "EXEC_STARTED", "ALL_DONE"]
"""Возможные статусы списка ордеров."""

type ListOrderStatus = Literal["EXECUTING", "ALL_DONE", "REJECT"]
"""Возможные статусы выполнения списка ордеров."""

type MarginType = Literal["ISOLATED", "CROSSED"]
"""Возможные типы маржи на фьючерсах."""

type IncomeType = Literal[
    "TRANSFER",
    "WELCOME_BONUS",
    "REALIZED_PNL",
    "FUNDING_FEE",
    "COMMISSION",
    "INSURANCE_CLEAR",
    "REFERRAL_KICKBACK",
    "COMMISSION_REBATE",
    "API_REBATE",
    "CONTEST_REWARD",
    "CROSS_COLLATERAL_TRANSFER",
    "OPTIONS_PREMIUM_FEE",
    "OPTIONS_SETTLE_PROFIT",
    "INTERNAL_TRANSFER",
    "AUTO_EXCHANGE",
    "DELIVERED_SETTELMENT",
    "COIN_SWAP_DEPOSIT",
    "COIN_SWAP_WITHDRAW",
    "POSITION_LIMIT_INCREASE_FEE",
]
"""Возможные типы доходов на фьючерсах."""

type FuturesTransferType = Literal["1", "2", "3", "4"]
"""Возможные типы переводов: 1-spot to futures, 2-futures to spot, 3-spot to delivery, 4-delivery to spot."""

type TransferType = Literal[
    "MAIN_UMFUTURE",
    "MAIN_CMFUTURE",
    "MAIN_MARGIN",
    "UMFUTURE_MAIN",
    "UMFUTURE_MARGIN",
    "CMFUTURE_MAIN",
    "CMFUTURE_MARGIN",
    "MARGIN_MAIN",
    "MARGIN_UMFUTURE",
    "MARGIN_CMFUTURE",
    "ISOLATEDMARGIN_MARGIN",
    "MARGIN_ISOLATEDMARGIN",
    "ISOLATEDMARGIN_ISOLATEDMARGIN",
    "MAIN_FUNDING",
    "FUNDING_MAIN",
    "FUNDING_UMFUTURE",
    "UMFUTURE_FUNDING",
    "MARGIN_FUNDING",
    "FUNDING_MARGIN",
    "FUNDING_CMFUTURE",
    "CMFUTURE_FUNDING",
    "MAIN_OPTION",
    "OPTION_MAIN",
    "UMFUTURE_OPTION",
    "OPTION_UMFUTURE",
    "MARGIN_OPTION",
    "OPTION_MARGIN",
]
"""Возможные типы внутренних переводов."""

type AccountType = Literal["SPOT", "MARGIN", "FUTURES"]
"""Возможные типы аккаунтов."""

type SymbolType = Literal["SPOT"]
"""Возможные типы символов на споте."""

type SymbolStatus = Literal[
    "PRE_TRADING", "TRADING", "POST_TRADING", "END_OF_DAY", "HALT", "AUCTION_MATCH", "BREAK"
]
"""Возможные статусы символов."""

type OrderBookType = Literal["NONE", "LIMIT", "LIMIT_MAKER", "STOP_LOSS_LIMIT"]
"""Возможные типы книги ордеров."""

type Permission = Literal[
    "SPOT",
    "MARGIN",
    "LEVERAGED",
    "TRD_GRP_002",
    "TRD_GRP_003",
    "TRD_GRP_004",
    "TRD_GRP_005",
    "TRD_GRP_006",
    "TRD_GRP_007",
    "TRD_GRP_008",
    "TRD_GRP_009",
    "TRD_GRP_010",
    "TRD_GRP_011",
    "TRD_GRP_012",
    "TRD_GRP_013",
]
"""Возможные разрешения для символов."""

type FuturesContractType = Literal[
    "PERPETUAL", "CURRENT_MONTH", "NEXT_MONTH", "CURRENT_QUARTER", "NEXT_QUARTER"
]
"""Возможные типы фьючерсных контрактов."""

type FuturesContractStatus = Literal[
    "PENDING_TRADING",
    "TRADING",
    "PRE_DELIVERING",
    "DELIVERING",
    "DELIVERED",
    "PRE_SETTLE",
    "SETTLING",
    "CLOSE",
]
"""Возможные статусы фьючерсных контрактов."""

type FuturesSymbolType = Literal["FUTURE"]
"""Возможные типы символов на фьючерсах."""

type FilterType = Literal[
    "PRICE_FILTER",
    "PERCENT_PRICE",
    "PERCENT_PRICE_BY_SIDE",
    "LOT_SIZE",
    "MIN_NOTIONAL",
    "NOTIONAL",
    "ICEBERG_PARTS",
    "MARKET_LOT_SIZE",
    "MAX_NUM_ORDERS",
    "MAX_NUM_ALGO_ORDERS",
    "MAX_NUM_ICEBERG_ORDERS",
    "MAX_POSITION",
    "TRAILING_DELTA",
]
"""Возможные типы фильтров символов."""

type PriceMatch = Literal[
    "OPPONENT",
    "OPPONENT_5",
    "OPPONENT_10",
    "OPPONENT_20",
    "QUEUE",
    "QUEUE_5",
    "QUEUE_10",
    "QUEUE_20",
]
"""Возможные типы ценовой совместимости."""

type AutoCloseType = Literal["LIQUIDATION", "ADL"]
"""Возможные типы автоматического закрытия позиции."""

type RollingWindowSize = Literal["1h", "4h", "1d"]
"""Возможные размеры окна для вебсокета статистики тикеров."""

type BookDepthLevels = Literal[5, 10, 20]
"""Возможные уровни глубины стакана."""

type MarkPriceUpdateSpeed = Literal["", "1s"]
"""Возможные скорости обновления для стрима futures mark price."""

type ContinuousContractType = Literal["perpetual", "current_quarter", "next_quarter"]
"""Возможные типы контрактов на для стрима continuous contract kline / candlestick streams."""
