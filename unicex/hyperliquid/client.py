__all__ = ["Client"]

import time
from typing import Any, Literal, Self

import aiohttp
import msgpack
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount
from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import LoggerLike
from unicex.utils import filter_params

# Authentication


def _l1_payload(phantom_agent: dict[str, Any]) -> dict[str, Any]:
    """Формирует EIP-712 payload для подписи "агента".

    Простыми словами:
    Это упаковка данных в формат, который кошелёк сможет подписать.
    В Ethereum есть стандарт EIP-712 — "structured data signing".
    Он позволяет подписывать не просто строку, а структуру (объект),
    чтобы потом её можно было проверить.

    Пример:
        >>> phantom = {"source": "a", "connectionId": b"1234...."}
        >>> _l1_payload(phantom)
        {...сложный словарь...}

    Параметры:
        phantom_agent (dict): объект с полями:
            - source (str): откуда пришёл агент ("a" для mainnet, "b" для testnet)
            - connectionId (bytes32): уникальный ID (обычно хэш)

    Возвращает:
        dict: структура для подписи через EIP-712
    """
    return {
        "domain": {
            "chainId": 1337,
            "name": "Exchange",
            "verifyingContract": "0x0000000000000000000000000000000000000000",
            "version": "1",
        },
        "types": {
            "Agent": [
                {"name": "source", "type": "string"},
                {"name": "connectionId", "type": "bytes32"},
            ],
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        },
        "primaryType": "Agent",
        "message": phantom_agent,
    }


def _address_to_bytes(address: str) -> bytes:
    r"""Переводит Ethereum-адрес в байты.

    Простыми словами:
    Берём строку вида "0xABC123..." и превращаем её в бинарные данные.
    Это нужно, потому что внутри подписи адрес должен храниться как массив байтов.

    Пример:
        >>> _address_to_bytes("0x0000000000000000000000000000000000000001")
        b'\\x00...\\x01'

    Параметры:
        address (str): строковый Ethereum-адрес, с "0x" или без.

    Возвращает:
        bytes: бинарное представление адреса.
    """
    return bytes.fromhex(address[2:] if address.startswith("0x") else address)


def _construct_phantom_agent(hash: bytes, is_mainnet: bool) -> dict[str, Any]:
    r"""Собирает объект "phantom_agent".

    Простыми словами:
    Это кусочек данных, который будет подписываться.
    В нём указывается:
    - источник ("a" если это mainnet, "b" если не mainnet)
    - connectionId — хэш действий.

    Пример:
        >>> _construct_phantom_agent(b"\\x01" * 32, True)
        {"source": "a", "connectionId": b"\\x01"*32}

    Параметры:
        hash (bytes): хэш действия (32 байта).
        is_mainnet (bool): True если сеть основная, False если тестовая.

    Возвращает:
        dict: объект phantom_agent.
    """
    return {"source": "a" if is_mainnet else "b", "connectionId": hash}


def _action_hash(
    action: dict[str, Any],
    vault_address: str | None,
    nonce: int,
    expires_after: int | None,
) -> bytes:
    r"""Строит хэш действия.

    Простыми словами:
    Берём действие (например, ордер), сериализуем его через msgpack,
    добавляем nonce, адрес хранилища (если есть), срок действия,
    и всё это хэшируем keccak256.
    Получается уникальный "отпечаток" действия.

    Пример:
        >>> action = {"type": "order", "amount": 1}
        >>> _action_hash(action, None, 42, None)
        b"\\xab...\\xff"   # 32 байта

    Параметры:
        action (dict): описание действия (например, ордер).
        vault_address (str | None): адрес кошелька/контракта, если есть.
        nonce (int): уникальный счётчик (чтобы нельзя было повторить действие).
        expires_after (int | None): время (в секундах), когда действие протухает.

    Возвращает:
        bytes: 32-байтовый хэш (keccak256).
    """
    data = msgpack.packb(action)
    data += nonce.to_bytes(8, "big")  # type: ignore
    if vault_address is None:
        data += b"\x00"
    else:
        data += b"\x01"
        data += _address_to_bytes(vault_address)
    if expires_after is not None:
        data += b"\x00"
        data += expires_after.to_bytes(8, "big")
    return keccak(data)


def _sign_inner(wallet: LocalAccount, data: dict[str, Any]) -> dict[str, Any]:
    """Подписывает данные EIP-712 через кошелёк.

    Простыми словами:
    Берём структуру (payload), кодируем её в формат EIP-712
    и просим кошелёк подписать.
    Возвращаем r, s, v — стандартные параметры Ethereum-подписи.

    Пример:
        >>> _sign_inner(wallet, {...})
        {"r": "0x...", "s": "0x...", "v": 27}

    Параметры:
        wallet (LocalAccount): объект кошелька.
        data (dict): структура для подписи (EIP-712).

    Возвращает:
        dict:
            - r (str): часть подписи
            - s (str): часть подписи
            - v (int): "восстановитель" (27 или 28 обычно)
    """
    structured_data = encode_typed_data(full_message=data)
    signed = wallet.sign_message(structured_data)
    return {"r": to_hex(signed["r"]), "s": to_hex(signed["s"]), "v": signed["v"]}


def _sign_l1_action(
    wallet: LocalAccount,
    action: dict[str, Any],
    active_pool: str | None,
    nonce: int,
    expires_after: int | None,
    is_mainnet: bool = True,
) -> dict[str, Any]:
    """Подписывает действие для L1 (основного уровня).

    Простыми словами:
    Это конечная функция, которая собирает всё:
    - делает хэш действия
    - строит phantom_agent
    - формирует payload для подписи
    - подписывает его через кошелёк
    Возвращает r, s, v.

    Пример:
        >>> _sign_l1_action(wallet, {"type": "order"}, None, 1, None, True)
        {"r": "0x...", "s": "0x...", "v": 27}

    Параметры:
        wallet (LocalAccount): объект кошелька.
        action (dict): действие (например, ордер).
        active_pool (str | None): адрес пула (если нужен).
        nonce (int): уникальный номер действия.
        expires_after (int | None): срок жизни действия.
        is_mainnet (bool): True — основная сеть, False — тестовая.

    Возвращает:
        dict:
            - r (str)
            - s (str)
            - v (int)
    """
    hash = _action_hash(action, active_pool, nonce, expires_after)
    phantom_agent = _construct_phantom_agent(hash, is_mainnet)
    data = _l1_payload(phantom_agent)
    return _sign_inner(wallet, data)


class Client(BaseClient):
    """Клиент для работы с Hyperliquid API."""

    _BASE_URL = "https://api.hyperliquid.xyz"
    """Базовый URL для REST API Hyperliquid."""

    _BASE_HEADERS = {"Content-Type": "application/json"}

    def __init__(
        self,
        session: aiohttp.ClientSession,
        private_key: str | bytes | None = None,
        wallet_address: str | None = None,
        vault_address: str | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            session (`aiohttp.ClientSession`): Сессия для выполнения HTTP‑запросов.
            private_key (`str | bytes | None`): Приватный ключ API для аутентификации (Hyperliquid).
            wallet_address (`str | None`): Адрес кошелька для аутентификации (Hyperliquid).
            vault_address (`str | None`): Адрес хранилища для аутентификации (Hyperliquid).
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера, сек.
        """
        super().__init__(
            session,
            None,
            None,
            None,
            logger,
            max_retries,
            retry_delay,
            proxies,
            timeout,
        )
        self._vault_address = vault_address
        self._wallet_address = wallet_address
        self._wallet: LocalAccount | None = None
        if private_key is not None:
            # private_key может быть в hex-строке ("0x...") или в байтах
            self._wallet = Account.from_key(private_key)

    @classmethod
    async def create(
        cls,
        private_key: str | bytes | None = None,
        wallet_address: str | None = None,
        vault_address: str | None = None,
        session: aiohttp.ClientSession | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        """Создаёт инстанцию клиента.

        Параметры:
            private_key (`str | bytes | None`): Приватный ключ для подписи запросов.
            wallet_address (`str | None`): Адрес кошелька для подписи запросов.
            vault_address (`str | None`): Адрес валита для подписи запросов.
            session (`aiohttp.ClientSession | None`): Сессия для HTTP‑запросов (если не передана, будет создана).
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимум повторов при ошибках запроса.
            retry_delay (`int | float`): Задержка между повторами, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси.
            timeout (`int`): Таймаут ответа сервера, сек.

        Возвращает:
            `Self`: Созданный экземпляр клиента.
        """
        return cls(
            private_key=private_key,
            wallet_address=wallet_address,
            vault_address=vault_address,
            session=session or aiohttp.ClientSession(),
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    async def _make_request(self, method: Literal["GET", "POST"], endpoint: str, data: dict) -> Any:
        """Создание HTTP-запроса к Hyperliquid API."""
        return await super()._make_request(
            method=method,
            url=self._BASE_URL + endpoint,
            headers=self._BASE_HEADERS,
            data=filter_params(data),
        )

    async def _post_request(self, endpoint: str, data: dict) -> Any:
        """Создание POST-запроса к Hyperliquid API."""
        return await self._make_request("POST", endpoint, data)

    # topic: Info endpoint
    # topic: Perpetuals

    async def perp_dexs(self) -> list[dict | None]:
        """Получение списка доступных перпетуальных DEX.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-metadata-universe-and-margin-tables
        """
        payload = {"type": "perpDexs"}

        return await self._post_request("/info", data=payload)

    async def perp_metadata(self, dex: str | None = None) -> dict:
        """Получение метаданных по перпетуальным контрактам.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-metadata-universe-and-margin-tables
        """
        payload = {
            "type": "meta",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def perp_meta_and_asset_contexts(self) -> list[dict | list]:
        """Получение метаданных и контекстов активов перпетуальных контрактов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-perpetuals-asset-contexts-includes-mark-price-current-funding-open-interest-etc
        """
        payload = {"type": "metaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def perp_account_summary(self, user: str, dex: str | None = None) -> dict:
        """Получение сводной информации по аккаунту пользователя в перпетуалах.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-users-perpetuals-account-summary
        """
        payload = {
            "type": "clearinghouseState",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def perp_user_funding_history(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list[dict]:
        """Получение истории фондирования пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-a-users-funding-history-or-non-funding-ledger-updates
        """
        payload = {
            "type": "userFunding",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def perp_user_non_funding_ledger_updates(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list[dict]:
        """Получение нефондировочных обновлений леджера пользователя.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-a-users-funding-history-or-non-funding-ledger-updates
        """
        payload = {
            "type": "userNonFundingLedgerUpdates",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def perp_funding_history(
        self,
        coin: str,
        start_time: int,
        end_time: int | None = None,
    ) -> list[dict]:
        """Получение исторических ставок фондирования по монете.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-historical-funding-rates
        """
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def perp_predicted_fundings(self) -> list[list[Any]]:
        """Получение предсказанных ставок фондирования по площадкам.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-predicted-funding-rates-for-different-venues
        """
        payload = {"type": "predictedFundings"}

        return await self._post_request("/info", data=payload)

    async def perps_at_open_interest_cap(self) -> list[str]:
        """Получение списка перпетуалов с достигнутым лимитом открытого интереса.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#query-perps-at-open-interest-caps
        """
        payload = {"type": "perpsAtOpenInterestCap"}

        return await self._post_request("/info", data=payload)

    async def perp_deploy_auction_status(self) -> dict:
        """Получение статуса аукциона развёртывания перпетуалов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-information-about-the-perp-deploy-auction
        """
        payload = {"type": "perpDeployAuctionStatus"}

        return await self._post_request("/info", data=payload)

    async def perp_active_asset_data(self, user: str, coin: str) -> dict:
        """Получение активных параметров актива пользователя в перпетуалах.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-users-active-asset-data
        """
        payload = {
            "type": "activeAssetData",
            "user": user,
            "coin": coin,
        }

        return await self._post_request("/info", data=payload)

    async def perp_dex_limits(self, dex: str) -> dict:
        """Получение лимитов для перпетуального DEX, развёрнутого билдерами.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals#retrieve-builder-deployed-perp-market-limits
        """
        payload = {
            "type": "perpDexLimits",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    # topic: Spot

    async def spot_metadata(self) -> dict:
        """Получение спотовой метаинформации о бирже.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-spot-metadata
        """
        payload = {"type": "spotMeta"}

        return await self._post_request("/info", data=payload)

    async def spot_meta_and_asset_contexts(self) -> list[dict | list]:
        """Получение метаданных и контекстов спотовых активов.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-spot-asset-contexts
        """
        payload = {"type": "spotMetaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def spot_token_balances(self, user: str) -> dict:
        """Получение балансов токенов пользователя на спотовом рынке.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-a-users-token-balances
        """
        payload = {
            "type": "spotClearinghouseState",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def spot_deploy_state(self, user: str) -> dict:
        """Получение информации об аукционе развёртывания спотового токена.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-the-spot-deploy-auction
        """
        payload = {
            "type": "spotDeployState",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def spot_pair_deploy_auction_status(self) -> dict:
        """Получение статуса аукциона развёртывания спотовых пар.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-the-spot-pair-deploy-auction
        """
        payload = {"type": "spotPairDeployAuctionStatus"}

        return await self._post_request("/info", data=payload)

    async def spot_token_details(self, token_id: str) -> dict:
        """Получение подробной информации о спотовом токене.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-information-about-a-token
        """
        payload = {
            "type": "tokenDetails",
            "tokenId": token_id,
        }

        return await self._post_request("/info", data=payload)

    # topic: Exchange endpoint

    async def place_order(
        self,
        asset: str,
        is_buy: bool,
        size: str,
        reduce_only: bool,
        order_type: Literal["limit", "trigger"],
        order_body: dict,
        price: str | None = None,
        client_order_id: str | None = None,
        grouping: Literal["na", "normalTpsl", "positionTpsl"] = "na",
        builder_address: str | None = None,
        builder_fee: int | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Выставление ордера на бирже.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#place-an-order
        """
        order_payload = {
            "a": asset,
            "b": is_buy,
            "p": price,
            "s": size,
            "r": reduce_only,
            "t": {order_type: order_body},
        }
        if client_order_id is not None:
            order_payload["c"] = client_order_id

        return await self.batch_place_orders(
            [order_payload],
            grouping=grouping,
            builder_address=builder_address,
            builder_fee=builder_fee,
            nonce=nonce,
            expires_after=expires_after,
            vault_address=vault_address,
        )

    async def batch_place_orders(
        self,
        orders: list[dict[str, Any]],
        grouping: Literal["na", "normalTpsl", "positionTpsl"] = "na",
        builder_address: str | None = None,
        builder_fee: int | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Пакетное выставление ордеров на бирже.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#place-an-order
        """
        if not orders:
            raise ValueError("orders must not be empty")
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")
        if builder_address is not None and builder_fee is None:
            raise TypeError("builder_fee is required when builder_address is provided")
        if builder_address is None and builder_fee is not None:
            raise TypeError("builder_address is required when builder_fee is provided")

        required_keys = {"a", "b", "p", "s", "r", "t"}
        normalized_orders = []
        for order in orders:
            missing_keys = required_keys - order.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise ValueError(f"order is missing required fields: {missing}")
            normalized = dict(order)
            normalized["p"] = str(normalized["p"])
            normalized["s"] = str(normalized["s"])
            if normalized.get("c") is None:
                normalized.pop("c", None)
            normalized_orders.append(normalized)

        action = {
            "type": "order",
            "orders": normalized_orders,
            "grouping": grouping,
        }
        if builder_address is not None:
            action["builder"] = {"b": builder_address, "f": builder_fee}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)
