__all__ = ["Client"]

from typing import Any

from unicex._base.asyncio import BaseClient
from unicex.types import RequestMethod

from .._mixins import ClientMixin
from ..types import (
    AssetType,
    BatchMode,
    BusinessType,
    KlineType,
    MergeDepthLimit,
    MergeDepthPrecision,
    OrderType,
    PlanType,
    Side,
    SpotGranularity,
    StpMode,
    TimeInForce,
    TpslType,
    TriggerType,
)


class Client(ClientMixin, BaseClient):
    """Клиент для работы с Bitget API."""

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bitget API.

        Если `signed=True`:
            - генерирует `timestamp` и `signature`;
            - добавляет авторизационные заголовки (`ACCESS-KEY`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`, `ACCESS-SIGN`).

        Если `signed=False`:
            - выполняет публичный запрос без подписи.

        Параметры:
            method (`RequestMethod`): HTTP-метод (`"GET"`, `"POST"`, и т. п.).
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/spot/v1/market/tickers"`).
            signed (`bool`): Приватный запрос (с подписью) или публичный. По умолчанию `False`.
            params (`dict[str, Any] | None`): Query-параметры запроса.
            data (`dict[str, Any] | None`): Тело запроса для `POST/PUT`.

        Возвращает:
            `Any`: Ответ API в формате JSON (`dict` или `list`), как вернул сервер.
        """
        url, params, data, headers = self._prepare_request_params(
            method=method,
            endpoint=endpoint,
            signed=signed,
            params=params,
            body=data,
        )
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    # ========== COMMON PUBLIC ==========

    async def server_time(self) -> dict:
        """Получение серверного времени.

        https://www.bitget.com/api-doc/common/intro
        """
        return await self._make_request("GET", "/api/v2/public/time")

    async def get_trade_rate(
        self,
        symbol: str,
        business: BusinessType,
    ) -> dict:
        """Получение торговой ставки (комиссии) для пары.

        https://www.bitget.com/api-doc/common/public/Get-Trade-Rate
        """
        params = {"symbol": symbol, "business": business}

        return await self._make_request("GET", "/api/v2/common/trade-rate", params=params)

    async def get_all_trade_rate(
        self,
        business: BusinessType,
    ) -> list[dict]:
        """Получение торговых ставок по всем парам для заданной линии.

        https://www.bitget.com/api-doc/common/public/Get-All-Trade-Rate
        """
        params = {"business": business}

        return await self._make_request("GET", "/api/v2/common/all-trade-rate", params=params)

    async def funding_assets(
        self,
        coin: str | None = None,
    ) -> list[dict]:
        """Получение информации о фандинговых активах (балансах).

        https://www.bitget.com/api-doc/common/account/Funding-Assets
        """
        params = {"coin": coin}

        return await self._make_request("GET", "/api/v2/account/funding-assets", params=params)

    async def all_account_balance(self) -> list[dict]:
        """Получение балансов по всем типам аккаунтов.

        https://www.bitget.com/api-doc/common/account/All-Account-Balance
        """
        return await self._make_request("GET", "/api/v2/account/all-account-balance")

    # ========== PUBLIC SPOT ENDPOINTS ==========

    async def get_coin_list(
        self,
        coin: str | None = None,
    ) -> list[dict]:
        """Получение списка монет (информация по валютам).

        https://www.bitget.com/api-doc/spot/market/Get-Coin-List
        """
        params = {"coin": coin}

        return await self._make_request("GET", "/api/v2/spot/public/coins", params=params)

    async def get_symbols(
        self,
        symbol: str | None = None,
    ) -> list[dict]:
        """Получение списка торговых пар / конфигураций символов.

        https://www.bitget.com/api-doc/spot/market/Get-Symbols
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/public/symbols", params=params)

    async def get_vip_fee_rate(self) -> list[dict]:
        """Получение VIP ставок комиссии на спотовом рынке.

        https://www.bitget.com/api-doc/spot/market/Get-VIP-Fee-Rate
        """
        return await self._make_request("GET", "/api/v2/spot/market/vip-fee-rate")

    async def get_tickers(
        self,
        symbol: str | None = None,
    ) -> list[dict]:
        """Получение информации по тикерам (все или конкретная пара).

        https://www.bitget.com/api-doc/spot/market/Get-Tickers
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/market/tickers", params=params)

    async def merge_orderbook(
        self,
        symbol: str,
        precision: MergeDepthPrecision | None = None,
        limit: MergeDepthLimit | None = None,
    ) -> dict:
        """Получение объединённой книги ордеров (merge depth).

        https://www.bitget.com/api-doc/spot/market/Merge-Orderbook
        """
        params = {
            "symbol": symbol,
            "precision": precision,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v2/spot/market/merge-depth", params=params)

    async def get_candle_data(
        self,
        symbol: str,
        granularity: SpotGranularity,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        kline_type: KlineType | None = None,
    ) -> list[list]:
        """Получение данных свечей (klines).

        https://www.bitget.com/api-doc/spot/market/Get-Candle-Data
        """
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "kLineType": kline_type,
        }

        return await self._make_request("GET", "/api/v2/spot/market/candles", params=params)

    async def get_auction(
        self,
        symbol: str,
    ) -> dict:
        """Получение аукционной информации (если поддерживается).

        https://www.bitget.com/api-doc/spot/market/Get-Auction
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/market/auction", params=params)

    async def get_history_candle_data(
        self,
        symbol: str,
        granularity: SpotGranularity,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических данных свечей.

        https://www.bitget.com/api-doc/spot/market/Get-History-Candle-Data
        """
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v2/spot/market/history-candles", params=params)

    async def get_recent_trades(
        self,
        symbol: str,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение последних совершённых сделок.

        https://www.bitget.com/api-doc/spot/market/Get-Recent-Trades
        """
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", "/api/v2/spot/market/fills", params=params)

    async def get_market_trades(
        self,
        symbol: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
    ) -> list[dict]:
        """Получение исторических сделок на рынке.

        https://www.bitget.com/api-doc/spot/market/Get-Market-Trades
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
        }

        return await self._make_request("GET", "/api/v2/spot/market/fills-history", params=params)

    # ========== PRIVATE SPOT ENDPOINTS ==========

    async def place_order(
        self,
        symbol: str,
        side: Side,
        order_type: OrderType,
        force: TimeInForce | None = None,
        price: str | None = None,
        size: str | None = None,
        client_oid: str | None = None,
        trigger_price: str | None = None,
        tpsl_type: TpslType | None = None,
        request_time: str | None = None,
        receive_window: str | None = None,
        stp_mode: StpMode | None = None,
        preset_take_profit_price: str | None = None,
        execute_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        execute_stop_loss_price: str | None = None,
    ) -> dict:
        """Размещение спотового ордера.

        https://www.bitget.com/api-doc/spot/trade/Place-Order
        """
        if order_type == "limit" and not force:
            raise TypeError("force is required for limit order")
        data = {
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "force": force,
            "price": price,
            "size": size,
            "clientOid": client_oid,
            "triggerPrice": trigger_price,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
            "stpMode": stp_mode,
            "presetTakeProfitPrice": preset_take_profit_price,
            "executeTakeProfitPrice": execute_take_profit_price,
            "presetStopLossPrice": preset_stop_loss_price,
            "executeStopLossPrice": execute_stop_loss_price,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/place-order", data=data, signed=True
        )

    async def cancel_replace_order(
        self,
        symbol: str,
        price: str,
        size: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_client_oid: str | None = None,
        preset_take_profit_price: str | None = None,
        execute_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        execute_stop_loss_price: str | None = None,
    ) -> dict:
        """Отмена существующего ордера и размещение нового.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Replace-Order
        """
        data = {
            "symbol": symbol,
            "price": price,
            "size": size,
            "orderId": order_id,
            "clientOid": client_oid,
            "newClientOid": new_client_oid,
            "presetTakeProfitPrice": preset_take_profit_price,
            "executeTakeProfitPrice": execute_take_profit_price,
            "presetStopLossPrice": preset_stop_loss_price,
            "executeStopLossPrice": execute_stop_loss_price,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-replace-order", data=data, signed=True
        )

    async def batch_cancel_replace_order(
        self,
        order_list: list[dict],
    ) -> list[dict]:
        """Пакетная отмена существующих ордеров и размещение новых.

        https://www.bitget.com/api-doc/spot/trade/Batch-Cancel-Replace-Order
        """
        data = {"orderList": order_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-replace-order", data=data, signed=True
        )

    async def cancel_order(
        self,
        symbol: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        tpsl_type: TpslType | None = None,
    ) -> dict:
        """Отмена спотового ордера.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Order
        """
        data = {
            "symbol": symbol,
            "orderId": order_id,
            "clientOid": client_oid,
            "tpslType": tpsl_type,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-order", data=data, signed=True
        )

    async def batch_place_orders(
        self,
        symbol: str,
        batch_mode: BatchMode | None = None,
        order_list: list[dict] | None = None,
    ) -> dict:
        """Пакетное размещение спотовых ордеров.

        https://www.bitget.com/api-doc/spot/trade/Batch-Place-Orders
        """
        if not order_list:
            raise TypeError("order_list is required")
        data = {"symbol": symbol, "orderList": order_list, "batchMode": batch_mode}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-orders", data=data, signed=True
        )

    async def batch_cancel_orders(
        self,
        symbol: str | None = None,
        batch_mode: BatchMode | None = None,
        order_list: list[dict] | None = None,
    ) -> dict:
        """Пакетная отмена спотовых ордеров.

        https://www.bitget.com/api-doc/spot/trade/Batch-Cancel-Orders
        """
        if not order_list:
            raise TypeError("order_list is required")
        data = {"symbol": symbol, "batchMode": batch_mode, "orderList": order_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-order", data=data, signed=True
        )

    async def cancel_symbol_orders(
        self,
        symbol: str,
    ) -> dict:
        """Отмена всех открытых ордеров по символу.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Symbol-Orders
        """
        data = {"symbol": symbol}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-symbol-order", data=data, signed=True
        )

    async def get_order_info(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> list[dict]:
        """Получение информации об ордере.

        https://www.bitget.com/api-doc/spot/trade/Get-Order-Info
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        params = {
            "orderId": order_id,
            "clientOid": client_oid,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/orderInfo", params=params, signed=True
        )

    async def get_unfilled_orders(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
        order_id: str | None = None,
        tpsl_type: TpslType | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> list[dict]:
        """Получение списка активных (не исполненных) ордеров.

        https://www.bitget.com/api-doc/spot/trade/Get-Unfilled-Orders
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
            "limit": limit,
            "orderId": order_id,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/unfilled-orders", params=params, signed=True
        )

    async def get_history_orders(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
        order_id: str | None = None,
        tpsl_type: TpslType | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> list[dict]:
        """Получение истории ордеров (за последние 90 дней).

        https://www.bitget.com/api-doc/spot/trade/Get-History-Orders
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
            "limit": limit,
            "orderId": order_id,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/history-orders", params=params, signed=True
        )

    async def get_fills(
        self,
        symbol: str | None = None,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> list[dict]:
        """Получение списка исполненных сделок (fills).

        https://www.bitget.com/api-doc/spot/trade/Get-Fills
        """
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "idLessThan": id_less_than,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/fills", params=params, signed=True
        )

    async def place_plan_order(
        self,
        symbol: str,
        side: Side,
        trigger_price: str,
        order_type: OrderType,
        size: str,
        trigger_type: TriggerType,
        execute_price: str | None = None,
        plan_type: PlanType | None = None,
        client_oid: str | None = None,
        stp_mode: StpMode | None = None,
    ) -> dict:
        """Размещение планового ордера (trigger / conditional order).

        https://www.bitget.com/api-doc/spot/plan/Place-Plan-Order
        """
        data = {
            "symbol": symbol,
            "side": side,
            "triggerPrice": trigger_price,
            "orderType": order_type,
            "size": size,
            "triggerType": trigger_type,
            "executePrice": execute_price,
            "planType": plan_type,
            "clientOid": client_oid,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/place-plan-order", data=data, signed=True
        )

    async def modify_plan_order(
        self,
        trigger_price: str,
        size: str,
        order_type: OrderType,
        order_id: str | None = None,
        client_oid: str | None = None,
        execute_price: str | None = None,
    ) -> dict:
        """Изменение планового ордера (trigger order).

        https://www.bitget.com/api-doc/spot/plan/Modify-Plan-Order
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        data = {
            "orderId": order_id,
            "clientOid": client_oid,
            "triggerPrice": trigger_price,
            "executePrice": execute_price,
            "size": size,
            "orderType": order_type,
        }

        return await self._make_request("POST", "/api/v2/spot/trade/modify-plan-order", data=data)

    async def cancel_plan_order(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict:
        """Отмена планового ордера.

        https://www.bitget.com/api-doc/spot/plan/Cancel-Plan-Order
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        data = {"orderId": order_id, "clientOid": client_oid}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-plan-order", data=data, signed=True
        )

    async def get_current_plan_orders(
        self,
        symbol: str,
        limit: int | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict:
        """Получение текущих плановых (trigger) ордеров.

        https://www.bitget.com/api-doc/spot/plan/Get-Current-Plan-Order
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/current-plan-order", params=params, signed=True
        )

    async def get_plan_sub_order(
        self,
        plan_order_id: str,
    ) -> list[dict]:
        """Получение списка суб-ордеров (исполненных частей планового ордера).

        https://www.bitget.com/api-doc/spot/plan/Get-Plan-Sub-Order
        """
        params = {"planOrderId": plan_order_id}

        return await self._make_request(
            "GET", "/api/v2/spot/trade/plan-sub-order", params=params, signed=True
        )

    async def get_history_plan_orders(
        self,
        symbol: str,
        start_time: int,
        end_time: int,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict:
        """Получение истории плановых ордеров (за период).

        https://www.bitget.com/api-doc/spot/plan/Get-History-Plan-Order
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "idLessThan": id_less_than,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/history-plan-order", params=params, signed=True
        )

    async def batch_cancel_plan_order(self, symbol_list: list[str]) -> dict:
        """Пакетная отмена плановых ордеров по списку символов.

        https://www.bitget.com/api-doc/spot/plan/Batch-Cancel-Plan-Order
        """
        data = {"symbolList": symbol_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-plan-order", data=data, signed=True
        )

    async def get_account_info(self) -> dict:
        """Получение информации об аккаунте.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Info
        """
        return await self._make_request("GET", "/api/v2/spot/account/info", signed=True)

    async def get_account_assets(
        self, coin: str | None = None, asset_type: AssetType | None = None
    ) -> list[dict]:
        """Получение списка активов на спотовом аккаунте.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Assets
        """
        params = {"coin": coin, "assetType": asset_type}

        return await self._make_request(
            "GET", "/api/v2/spot/account/asset", signed=True, params=params
        )

    # ========== PUBLIC FUTURES ENDPOINTS ==========

    # ========== PRIVATE FUTURES ENDPOINTS ==========
