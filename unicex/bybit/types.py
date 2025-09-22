from typing import Literal

type Timeframe = Literal[
    "1",
    "3",
    "5",
    "15",
    "30",
    "60",
    "120",
    "240",
    "360",
    "720",
    "D",
    "W",
    "M",
]
"""Возможные интервалы для запросов исторических данных."""

type Category = Literal["linear", "inverse", "spot", "option"]
"""Возможные категории продуктов."""

type FuturesCategory = Literal["linear", "inverse"]
"""Возможные категории фьючерсных продуктов."""

type DerivativesCategory = Literal["linear", "inverse", "option"]
"""Возможные категории деривативов."""

type Side = Literal["Buy", "Sell"]
"""Возможные стороны для торговли."""

type OrderType = Literal[
    "Market",
    "Limit",
    "Conditional",
]
"""Возможные типы ордеров."""

type TimeInForce = Literal["GTC", "IOC", "FOK", "PostOnly", "RPI"]
"""Возможные стратегии времени действия ордера."""

type OrderStatus = Literal[
    "New",
    "PartiallyFilled",
    "Filled",
    "Cancelled",
    "Rejected",
    "PartiallyFilledCanceled",
    "Deactivated",
    "Triggered",
    "Untriggered",
    "Active",
]
"""Возможные статусы ордеров."""

type OrderFilter = Literal["Order", "tpslOrder", "StopOrder"]
"""Фильтры типов ордеров для спота."""

type TriggerBy = Literal["LastPrice", "IndexPrice", "MarkPrice"]
"""Типы цен для триггера условных ордеров."""

type PositionIdx = Literal[0, 1, 2]
"""Индексы позиций: 0 - одностороння, 1 - хедж Buy, 2 - хедж Sell."""

# ========== SLIPPAGE ==========

type SlippageToleranceType = Literal["TickSize", "Percent"]
"""Типы толерантности к проскальзыванию."""

# ========== TAKE PROFIT / STOP LOSS ==========

type TpSlMode = Literal["Full", "Partial"]
"""Режимы работы Take Profit / Stop Loss."""

type TpSlOrderType = Literal["Market", "Limit"]
"""Типы ордеров для TP/SL."""

# ========== POSITIONS ==========

type PositionSide = Literal["Buy", "Sell", "None"]
"""Стороны позиций."""

type MarginMode = Literal["ISOLATED_MARGIN", "REGULAR_MARGIN", "PORTFOLIO_MARGIN"]
"""Режимы маржи."""

# ========== ACCOUNT ==========

type AccountType = Literal["UNIFIED", "NORMAL", "FUND"]
"""Типы аккаунтов."""

type UnifiedMarginStatus = Literal["1", "2", "3", "4"]
"""Статусы объединенной маржи."""

# ========== TRANSFERS ==========

type TransferStatus = Literal["SUCCESS", "PENDING", "FAILED"]
"""Статусы переводов."""

type AccountType_Transfer = Literal["FUND", "UNIFIED", "SPOT", "CONTRACT", "OPTION"]
"""Типы аккаунтов для переводов."""

# ========== MARKET UNIT ==========

type MarketUnit = Literal["baseCoin", "quoteCoin"]
"""Единицы измерения для рыночных ордеров на споте."""

# ========== SMP (Self-Match Prevention) ==========

type SmpType = Literal["None", "CancelMaker", "CancelTaker", "CancelBoth"]
"""Типы предотвращения самопересечения."""

# ========== WALLET ==========

type CoinType = Literal["FUND", "UNIFIED"]
"""Типы кошельков."""

# ========== LEVERAGE ==========

type LeverageTokenLimitType = Literal["PurchaseLimit", "RedemptionLimit"]
"""Типы лимитов для токенов с кредитным плечом."""

# ========== INSURANCE ==========

type InsuranceCoin = Literal["BTC", "USDT"]
"""Монеты страхового фонда."""

# ========== HISTORICAL DATA ==========

type DataRecordingPeriod = Literal["5min", "15min", "30min", "1h", "4h", "1d"]
"""Периоды записи исторических данных."""

# ========== ANNOUNCEMENT ==========

type AnnouncementType = Literal["new_crypto", "delist", "latest"]
"""Типы объявлений."""

type AnnouncementTag = Literal[
    "Spot",
    "Derivatives",
    "Options",
    "Leveraged_Tokens",
    "Launchpad",
    "Launchpool",
    "Spot_Listings",
    "VIP",
    "Margin_Trading",
    "P2P",
    "Trading_Bots",
]
"""Теги объявлений."""

# ========== RISK LIMIT ==========

type RiskLimitCategory = Literal["linear", "inverse"]
"""Категории для риск лимитов."""

# ========== DELIVERY PRICE ==========

type DeliveryPriceCategory = Literal["linear", "inverse", "option"]
"""Категории для цен поставки."""

# ========== FUNDING ==========

type FundingIntervalCategory = Literal["linear", "inverse"]
"""Категории для интервалов фондирования."""

# ========== OPTIONS ==========

type OptionType = Literal["Call", "Put"]
"""Типы опционов."""

# ========== EXECUTION TYPES ==========

type ExecType = Literal[
    "Trade", "AdlTrade", "Funding", "BustTrade", "Settle", "Delivery", "BlockTrade", "MovePosition"
]
"""Типы исполнения сделок."""

# ========== INTERVALS FOR STATISTICS ==========

type StatsInterval = Literal["5min", "15min", "30min", "1h", "4h", "1d"]
"""Интервалы для статистики."""

# ========== API KEY PERMISSIONS ==========

type Permission = Literal[
    "ContractTrade",
    "Spot",
    "Wallet",
    "Options",
    "Derivatives",
    "CopyTrading",
    "BlockTrade",
    "Exchange",
    "NFT",
]
"""Разрешения для API ключей."""

# ========== UNIFIED UPGRADE STATUS ==========

type UpgradeStatus = Literal["0", "1", "2", "3", "4", "5"]
"""Статусы обновления до единого аккаунта."""

# ========== BORROWING ==========

type InterestBearingBorrowSize = Literal["0", "1"]
"""Размер заимствования под проценты."""

# ========== INSTITUTIONAL LENDING ==========

type LendingProductType = Literal["FLEX_TERM", "FIXED_TERM"]
"""Типы продуктов институционального кредитования."""

type LendingOrderStatus = Literal["1", "2", "3", "4", "5", "6"]
"""Статусы ордеров институционального кредитования."""

# ========== C2C LENDING ==========

type LendingOrderType = Literal["1", "2"]
"""Типы ордеров C2C кредитования."""

# ========== CONVERT ==========

type ConvertStatus = Literal["init", "processing", "success", "failure"]
"""Статусы конвертации."""

# ========== PRE-UPGRADE ==========

type UpgradeToUTAStatus = Literal["0", "1", "2", "3"]
"""Статусы предварительного обновления до UTA."""

# ========== RESPONSE FORMATS ==========

type RetCode = Literal[
    0, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10009, 10010, 10016, 10017, 10018
]
"""Коды возврата API."""

# ========== WEBSOCKET ==========

type WSMessageType = Literal["snapshot", "delta"]
"""Типы сообщений WebSocket."""

type WSOperation = Literal["subscribe", "unsubscribe", "ping", "pong"]
"""Операции WebSocket."""

type WSTopicType = Literal[
    "orderbook", "publicTrade", "ticker", "kline", "liquidation", "ltNav", "ltTicker", "ltKline"
]
"""Типы публичных топиков WebSocket."""

type WSPrivateTopicType = Literal["position", "execution", "order", "wallet", "greeks"]
"""Типы приватных топиков WebSocket."""

# ========== DEPOSIT/WITHDRAW ==========

type DepositStatus = Literal["0", "1", "2", "3", "4"]
"""Статусы депозитов."""

type WithdrawStatus = Literal[
    "SecurityCheck", "Pending", "success", "CancelByUser", "Reject", "Fail", "MoreInformation"
]
"""Статусы выводов средств."""

type WithdrawType = Literal["0", "1", "2"]
"""Типы выводов: 0-on-chain, 1-internal, 2-off-chain."""
