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


def _user_signed_payload(
    primary_type: str,
    payload_types: list[dict[str, str]],
    action: dict[str, Any],
) -> dict[str, Any]:
    """Формирует EIP-712 payload для "user-signed" подписи.

    Простыми словами:
    Это структура для подписи действий от лица пользователя.
    В отличие от L1-подписи (где используется phantom-агент),
    здесь кошелёк подписывает само действие напрямую.

    ChainID и домен указываются специально, чтобы предотвратить
    повторное воспроизведение (replay) на других цепях.

    Пример:
        >>> payload = _user_signed_payload(
        ...     primary_type="Withdraw",
        ...     payload_types=[{"name": "amount", "type": "uint256"}],
        ...     action={"amount": 100, "signatureChainId": "0x66eee"},
        ... )
        >>> payload.keys()
        dict_keys(["domain", "types", "primaryType", "message"])

    Параметры:
        primary_type (str): Основной тип сообщения, например `"Withdraw"`, `"Transfer"`.
        payload_types (list[dict]): Список полей EIP-712 типа, например:
            `[{"name": "amount", "type": "uint256"}, {"name": "recipient", "type": "address"}]`
        action (dict): Само сообщение (поля, которые будут подписаны).
            Должно содержать `"signatureChainId"` (строку в hex).

    Возвращает:
        dict: Полностью готовая структура EIP-712 для подписи кошельком.
    """
    chain_id = int(action["signatureChainId"], 16)
    return {
        "domain": {
            "name": "HyperliquidSignTransaction",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": "0x0000000000000000000000000000000000000000",
        },
        "types": {
            primary_type: payload_types,
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        },
        "primaryType": primary_type,
        "message": action,
    }


def _sign_user_signed_action(
    wallet: LocalAccount,
    action: dict[str, Any],
    payload_types: list[dict[str, str]],
    primary_type: str,
    is_mainnet: bool,
) -> dict[str, Any]:
    """Подписывает действие "user-signed" формата (EIP-712).

    Простыми словами:
    Это альтернатива L1-подписи. Здесь сам пользователь (его кошелёк)
    подписывает объект `action`, который будет исполнен Hyperliquid.
    Отличие от L1: используется другой `chainId` (0x66eee) и поле `"hyperliquidChain"`,
    чтобы действие нельзя было воспроизвести в другой сети.

    Пример:
        >>> action = {"amount": 100}
        >>> payload_types = [{"name": "amount", "type": "uint256"}]
        >>> sig = _sign_user_signed_action(wallet, action, payload_types, "Withdraw", True)
        >>> sig.keys()
        dict_keys(["r", "s", "v"])

    Параметры:
        wallet (LocalAccount): Объект кошелька, созданный через `Account.from_key(...)`.
        action (dict): Содержимое действия, которое нужно подписать.
        payload_types (list[dict[str, str]]): Описание полей типа для EIP-712.
        primary_type (str): Основное имя типа, например `"Withdraw"`, `"Transfer"`.
        is_mainnet (bool): True — подпись для основной сети, False — для тестовой.

    Возвращает:
        dict:
            - r (str): первая часть подписи
            - s (str): вторая часть подписи
            - v (int): "восстановитель" подписи (27 или 28)
    """
    # signatureChainId — цепочка, через которую кошелёк делает подпись (не Hyperliquid chain)
    action["signatureChainId"] = "0x66eee"
    # hyperliquidChain — фактическая среда исполнения
    action["hyperliquidChain"] = "Mainnet" if is_mainnet else "Testnet"

    data = _user_signed_payload(primary_type, payload_types, action)
    return _sign_inner(wallet, data)


USD_SEND_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "time", "type": "uint64"},
]

SPOT_TRANSFER_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "token", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "time", "type": "uint64"},
]

WITHDRAW_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "time", "type": "uint64"},
]

USD_CLASS_TRANSFER_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "toPerp", "type": "bool"},
    {"name": "nonce", "type": "uint64"},
]

SEND_ASSET_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "destination", "type": "string"},
    {"name": "sourceDex", "type": "string"},
    {"name": "destinationDex", "type": "string"},
    {"name": "token", "type": "string"},
    {"name": "amount", "type": "string"},
    {"name": "fromSubAccount", "type": "string"},
    {"name": "nonce", "type": "uint64"},
]

STAKING_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "wei", "type": "uint64"},
    {"name": "nonce", "type": "uint64"},
]

TOKEN_DELEGATE_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "validator", "type": "address"},
    {"name": "wei", "type": "uint64"},
    {"name": "isUndelegate", "type": "bool"},
    {"name": "nonce", "type": "uint64"},
]

APPROVE_AGENT_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "agentAddress", "type": "address"},
    {"name": "agentName", "type": "string"},
    {"name": "nonce", "type": "uint64"},
]

APPROVE_BUILDER_FEE_SIGN_TYPES = [
    {"name": "hyperliquidChain", "type": "string"},
    {"name": "maxFeeRate", "type": "string"},
    {"name": "builder", "type": "address"},
    {"name": "nonce", "type": "uint64"},
]


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

    async def _make_request(
        self,
        method: Literal["GET", "POST"],
        endpoint: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Создаёт HTTP-запрос к Hyperliquid API.

        Параметры:
            method (`Literal["GET", "POST"]`): HTTP-метод запроса.
            endpoint (`str`): Относительный путь эндпоинта.
            data (`dict[str, Any] | None`): Тело запроса для POST-запросов.

        Возвращает:
          `Any`: Ответ Hyperliquid API.
        """
        filtered_data = filter_params(data) if data is not None else None

        return await super()._make_request(
            method=method,
            url=self._BASE_URL + endpoint,
            headers=self._BASE_HEADERS,
            data=filtered_data,
        )

    async def _post_request(self, endpoint: str, data: dict) -> Any:
        """Создание POST-запроса к Hyperliquid API."""
        return await self._make_request("POST", endpoint, data=data)

    async def request(
        self,
        endpoint: str,
        *,
        data: dict,
    ) -> Any:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            endpoint (`str`): Относительный путь эндпоинта (например, `/info`).
            data (`dict[str, Any]`): JSON-тело запроса для POST-запросов.

        Возвращает:
          `Any`: Ответ Hyperliquid API.
        """
        return await self._post_request(endpoint, data=data)

    # topic: Info endpoint
    # topic: Futures

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

    async def perp_meta_and_asset_contexts(self) -> list[Any]:
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

    async def open_orders(self, user: str, dex: str | None = None) -> list[dict]:
        """Получение списка открытых ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-openorders
        """
        payload = {
            "type": "openOrders",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def exchange_status(self) -> dict:
        """Получение текущего статуса биржи Hyperliquid.

        https://docs.chainstack.com/reference/hyperliquid-info-exchangestatus
        """
        payload = {"type": "exchangeStatus"}

        return await self._post_request("/info", data=payload)

    async def frontend_open_orders(self, user: str, dex: str | None = None) -> list[dict]:
        """Получение открытых ордеров в формате фронтенда.

        https://docs.chainstack.com/reference/hyperliquid-info-frontendopenorders
        """
        payload = {
            "type": "frontendOpenOrders",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def liquidatable(self, user: str) -> dict:
        """Проверка, подлежит ли аккаунт пользователя ликвидации.

        https://docs.chainstack.com/reference/hyperliquid-info-liquidatable
        """
        payload = {
            "type": "liquidatable",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def max_market_order_ntls(self) -> list[dict]:
        """Получение максимальных объёмов рыночных ордеров по активам.

        https://docs.chainstack.com/reference/hyperliquid-info-maxmarketorderntls
        """
        payload = {"type": "maxMarketOrderNtls"}

        return await self._post_request("/info", data=payload)

    async def vault_summaries(self) -> list[dict]:
        """Получение сводки по всем доступным вултам (vaults).

        https://docs.chainstack.com/reference/hyperliquid-info-vaultsummaries
        """
        payload = {"type": "vaultSummaries"}

        return await self._post_request("/info", data=payload)

    async def user_vault_equities(self, user: str) -> list[dict]:
        """Получение данных об инвестициях пользователя в вулты (vaults).

        https://docs.chainstack.com/reference/hyperliquid-info-uservaultequities
        """
        payload = {
            "type": "userVaultEquities",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def leading_vaults(self, user: str) -> list[dict]:
        """Получение списка вултов (vaults), которыми управляет пользователь.

        https://docs.chainstack.com/reference/hyperliquid-info-leadingvaults
        """
        payload = {
            "type": "leadingVaults",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def extra_agents(self, user: str) -> list[dict]:
        """Получение списка дополнительных агентов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-extraagents
        """
        payload = {
            "type": "extraAgents",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def sub_accounts(self, user: str) -> list[dict]:
        """Получение списка саб-аккаунтов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-subaccounts
        """
        payload = {
            "type": "subAccounts",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_fees(self, user: str) -> dict:
        """Получение информации о торговых комиссиях пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-userfees
        """
        payload = {
            "type": "userFees",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_rate_limit(self, user: str) -> dict:
        """Получение сведений о лимитах запросов пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-userratelimit
        """
        payload = {
            "type": "userRateLimit",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def delegations(self, user: str) -> list[dict]:
        """Получение списка делегаций пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegations
        """
        payload = {
            "type": "delegations",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def delegator_summary(self, user: str) -> dict:
        """Получение сводки по делегациям пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegator-summary
        """
        payload = {
            "type": "delegatorSummary",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def max_builder_fee(self, user: str, builder: str) -> int:
        """Получение максимальной комиссии билдера, одобренной пользователем.

        https://docs.chainstack.com/reference/hyperliquid-info-max-builder-fee
        """
        payload = {
            "type": "maxBuilderFee",
            "user": user,
            "builder": builder,
        }

        return await self._post_request("/info", data=payload)

    async def user_to_multi_sig_signers(self, user: str) -> list[str]:
        """Получение списка подписантов мультисиг-кошелька пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-to-multi-sig-signers
        """
        payload = {
            "type": "userToMultiSigSigners",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_role(self, user: str) -> dict:
        """Получение информации о роли пользователя в системе.

        https://docs.chainstack.com/reference/hyperliquid-info-user-role
        """
        payload = {
            "type": "userRole",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def validator_l1_votes(self) -> list[dict]:
        """Получение сведений о голосах валидаторов на L1.

        https://docs.chainstack.com/reference/hyperliquid-info-validator-l1-votes
        """
        payload = {"type": "validatorL1Votes"}

        return await self._post_request("/info", data=payload)

    async def web_data2(self) -> dict:
        """Получение агрегированных данных для веб-интерфейса.

        https://docs.chainstack.com/reference/hyperliquid-info-web-data2
        """
        payload = {"type": "webData2"}

        return await self._post_request("/info", data=payload)

    async def all_mids(self, dex: str | None = None) -> dict:
        """Получение текущих средних цен по всем активам.

        https://docs.chainstack.com/reference/hyperliquid-info-allmids
        """
        payload = {
            "type": "allMids",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def user_fills(
        self,
        user: str,
        aggregate_by_time: bool | None = None,
    ) -> list[dict]:
        """Получение последних исполнений ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-fills
        """
        payload = {
            "type": "userFills",
            "user": user,
            "aggregateByTime": aggregate_by_time,
        }

        return await self._post_request("/info", data=payload)

    async def user_fills_by_time(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
        aggregate_by_time: bool | None = None,
    ) -> list[dict]:
        """Получение исполнений ордеров пользователя за период.

        https://docs.chainstack.com/reference/hyperliquid-info-user-fills-by-time
        """
        payload = {
            "type": "userFillsByTime",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
            "aggregateByTime": aggregate_by_time,
        }

        return await self._post_request("/info", data=payload)

    async def order_status(self, user: str, oid: int | str) -> dict:
        """Получение статуса ордера по идентификатору.

        https://docs.chainstack.com/reference/hyperliquid-info-order-status
        """
        payload = {
            "type": "orderStatus",
            "user": user,
            "oid": oid,
        }

        return await self._post_request("/info", data=payload)

    async def l2_book(
        self,
        coin: str,
        n_sig_figs: Literal[2, 3, 4, 5] | None = None,
        mantissa: Literal[1, 2, 5] | None = None,
    ) -> list[list[dict]]:
        """Получение снапшота стакана уровня L2 для актива.

        https://docs.chainstack.com/reference/hyperliquid-info-l2-book
        """
        payload = {
            "type": "l2Book",
            "coin": coin,
            "nSigFigs": n_sig_figs,
            "mantissa": mantissa,
        }

        return await self._post_request("/info", data=payload)

    async def batch_clearinghouse_states(
        self,
        users: list[str],
        dex: str | None = None,
    ) -> list[dict | None]:
        """Получение сводок фьючерсных аккаунтов группы пользователей.

        https://docs.chainstack.com/reference/hyperliquid-info-batch-clearinghouse-states
        """
        payload = {
            "type": "batchClearinghouseStates",
            "users": users,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def candle_snapshot(
        self,
        coin: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        """Получение датасета свечей за указанный период.

        https://docs.chainstack.com/reference/hyperliquid-info-candle-snapshot
        """
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": coin,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
            },
        }

        return await self._post_request("/info", data=payload)

    async def historical_orders(self, user: str) -> list[dict]:
        """Получение истории ордеров пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-historical-orders
        """
        payload = {
            "type": "historicalOrders",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def user_twap_slice_fills(self, user: str) -> list[dict]:
        """Получение последних TWAP-исполнений пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-twap-slice-fills
        """
        payload = {
            "type": "userTwapSliceFills",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def recent_trades(self, coin: str) -> list[dict]:
        """Получение последних публичных сделок по активу.

        https://docs.chainstack.com/reference/hyperliquid-info-recent-trades
        """
        payload = {
            "type": "recentTrades",
            "coin": coin,
        }

        return await self._post_request("/info", data=payload)

    async def vault_details(self, vault_address: str, user: str | None = None) -> dict:
        """Получение подробной информации о выбранном вулте.

        https://docs.chainstack.com/reference/hyperliquid-info-vault-details
        """
        payload = {
            "type": "vaultDetails",
            "vaultAddress": vault_address,
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def portfolio(self, user: str) -> list[list[Any]]:
        """Получение данных о производительности портфеля пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-portfolio
        """
        payload = {
            "type": "portfolio",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def referral(self, user: str) -> dict:
        """Получение реферальной информации пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-referral
        """
        payload = {
            "type": "referral",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def delegator_rewards(self, user: str) -> list[dict]:
        """Получение истории стейкинг-наград пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-delegator-rewards
        """
        payload = {
            "type": "delegatorRewards",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def gossip_root_ips(self) -> list[str]:
        """Получение списка узлов для P2P-госсипа.

        https://docs.chainstack.com/reference/hyperliquid-info-gossip-root-ips
        """
        payload = {"type": "gossipRootIps"}

        return await self._post_request("/info", data=payload)

    # topic: Spot

    async def spot_metadata(self) -> dict:
        """Получение спотовой метаинформации о бирже.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot#retrieve-spot-metadata
        """
        payload = {"type": "spotMeta"}

        return await self._post_request("/info", data=payload)

    async def spot_meta_and_asset_contexts(self) -> list[Any]:
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
        asset: int,
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

    async def cancel_order(
        self,
        asset: int,
        order_id: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Отмена ордера по идентификатору.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-order-s
        """
        return await self.cancel_orders(
            cancels=[{"a": asset, "o": order_id}],
            nonce=nonce,
            expires_after=expires_after,
            vault_address=vault_address,
        )

    async def cancel_orders(
        self,
        cancels: list[dict[str, int | str]],
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Отмена ордеров по идентификатору ордера.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-order-s
        """
        if not cancels:
            raise ValueError("cancels must not be empty")
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        normalized: list[dict[str, int]] = []
        for cancel in cancels:
            missing_keys = {"a", "o"} - cancel.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise ValueError(f"cancel entry is missing required fields: {missing}")
            normalized.append(
                {
                    "a": int(cancel["a"]),
                    "o": int(cancel["o"]),
                }
            )

        action = {"type": "cancel", "cancels": normalized}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def cancel_order_by_cloid(
        self,
        asset: int,
        client_order_id: str,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Отмена ордера по клиентскому идентификатору.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-order-s-by-cloid
        """
        return await self.cancel_orders_by_cloid(
            cancels=[{"asset": asset, "cloid": client_order_id}],
            nonce=nonce,
            expires_after=expires_after,
            vault_address=vault_address,
        )

    async def cancel_orders_by_cloid(
        self,
        cancels: list[dict[str, Any]],
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Отмена ордеров по клиентскому идентификатору.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-order-s-by-cloid
        """
        if not cancels:
            raise ValueError("cancels must not be empty")
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        normalized: list[dict[str, Any]] = []
        for cancel in cancels:
            missing_keys = {"asset", "cloid"} - cancel.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise ValueError(f"cancel entry is missing required fields: {missing}")
            normalized.append(
                {
                    "asset": int(cancel["asset"]),
                    "cloid": str(cancel["cloid"]),
                }
            )

        action = {"type": "cancelByCloid", "cancels": normalized}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def schedule_cancel(
        self,
        time_ms: int | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Планирование массовой отмены ордеров.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#schedule-cancel-dead-mans-switch
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action: dict[str, Any] = {"type": "scheduleCancel"}
        if time_ms is not None:
            action["time"] = time_ms

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def modify_order(
        self,
        order_id: int | str,
        asset: int,
        is_buy: bool,
        price: str | float,
        size: str | float,
        reduce_only: bool,
        order_type: Literal["limit", "trigger"],
        order_body: dict[str, Any],
        client_order_id: str | None = None,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Модификация существующего ордера.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#modify-an-order
        """
        order_payload: dict[str, Any] = {
            "a": asset,
            "b": is_buy,
            "p": str(price),
            "s": str(size),
            "r": reduce_only,
            "t": {order_type: order_body},
        }
        if client_order_id is not None:
            order_payload["c"] = client_order_id

        return await self.batch_modify_orders(
            modifies=[{"oid": order_id, "order": order_payload}],
            nonce=nonce,
            expires_after=expires_after,
            vault_address=vault_address,
        )

    async def batch_modify_orders(
        self,
        modifies: list[dict[str, Any]],
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Пакетная модификация ордеров.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#modify-multiple-orders
        """
        if not modifies:
            raise ValueError("modifies must not be empty")
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        normalized: list[dict[str, Any]] = []
        for modify in modifies:
            missing_keys = {"oid", "order"} - modify.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise ValueError(f"modify entry is missing required fields: {missing}")
            order = dict(modify["order"])
            required_order_keys = {"a", "b", "p", "s", "r", "t"}
            missing_order_keys = required_order_keys - order.keys()
            if missing_order_keys:
                missing = ", ".join(sorted(missing_order_keys))
                raise ValueError(f"order payload is missing required fields: {missing}")
            order["p"] = str(order["p"])
            order["s"] = str(order["s"])
            if order.get("c") is None:
                order.pop("c", None)
            normalized.append(
                {
                    "oid": modify["oid"],
                    "order": order,
                }
            )

        action = {"type": "batchModify", "modifies": normalized}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def update_leverage(
        self,
        asset: int,
        is_cross: bool,
        leverage: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Обновление кредитного плеча по активу.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#update-leverage
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "updateLeverage",
            "asset": asset,
            "isCross": is_cross,
            "leverage": leverage,
        }

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def update_isolated_margin(
        self,
        asset: int,
        is_buy: bool,
        notional_change: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Обновление маржи изолированной позиции.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#update-isolated-margin
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "updateIsolatedMargin",
            "asset": asset,
            "isBuy": is_buy,
            "ntli": notional_change,
        }

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def usd_send(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        destination: str,
        amount: str,
        time_ms: int,
        nonce: int | None = None,
    ) -> dict:
        """Перевод USDC между пользователями Hyperliquid.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#core-usdc-transfer
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "usdSend",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "destination": destination,
            "amount": amount,
            "time": time_ms,
        }
        action_nonce = nonce if nonce is not None else time_ms
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            USD_SEND_SIGN_TYPES,
            "HyperliquidTransaction:UsdSend",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def spot_send(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        destination: str,
        token: str,
        amount: str,
        time_ms: int,
        nonce: int | None = None,
    ) -> dict:
        """Перевод спотового актива между пользователями Hyperliquid.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#core-spot-transfer
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "spotSend",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "destination": destination,
            "token": token,
            "amount": amount,
            "time": time_ms,
        }
        action_nonce = nonce if nonce is not None else time_ms
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            SPOT_TRANSFER_SIGN_TYPES,
            "HyperliquidTransaction:SpotSend",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def initiate_withdrawal(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        amount: str,
        time_ms: int,
        destination: str,
        nonce: int | None = None,
    ) -> dict:
        """Инициация вывода средств на L1.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#initiate-a-withdrawal-request
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "withdraw3",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "amount": amount,
            "time": time_ms,
            "destination": destination,
        }
        action_nonce = nonce if nonce is not None else time_ms
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            WITHDRAW_SIGN_TYPES,
            "HyperliquidTransaction:Withdraw",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def usd_class_transfer(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        amount: str,
        to_perp: bool,
        subaccount: str | None = None,
    ) -> dict:
        """Перевод USDC между спотовым и перпетуальным аккаунтами.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#transfer-from-spot-account-to-perp-account-and-vice-versa
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        amount_field = amount
        if subaccount is not None:
            amount_field = f"{amount} subaccount:{subaccount}"

        nonce = int(time.time() * 1000)

        action = {
            "type": "usdClassTransfer",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "amount": amount_field,
            "toPerp": to_perp,
            "nonce": nonce,
        }
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            USD_CLASS_TRANSFER_SIGN_TYPES,
            "HyperliquidTransaction:UsdClassTransfer",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def send_asset(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        destination: str,
        source_dex: str,
        destination_dex: str,
        token: str,
        amount: str,
        from_subaccount: str,
        nonce_value: int,
        nonce: int | None = None,
    ) -> dict:
        """Перевод токена между балансами и субаккаунтами (тестнет).

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#send-asset-testnet-only
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "sendAsset",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "destination": destination,
            "sourceDex": source_dex,
            "destinationDex": destination_dex,
            "token": token,
            "amount": amount,
            "fromSubAccount": from_subaccount,
            "nonce": nonce_value,
        }
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            SEND_ASSET_SIGN_TYPES,
            "HyperliquidTransaction:SendAsset",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def staking_deposit(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        wei_amount: int,
        nonce_value: int,
        nonce: int | None = None,
    ) -> dict:
        """Депозит нативного токена в стейкинг.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#deposit-into-staking
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "cDeposit",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "wei": wei_amount,
            "nonce": nonce_value,
        }
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            STAKING_SIGN_TYPES,
            "HyperliquidTransaction:CDeposit",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def staking_withdraw(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        wei_amount: int,
        nonce_value: int,
        nonce: int | None = None,
    ) -> dict:
        """Вывод нативного токена из стейкинга.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#withdraw-from-staking
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "cWithdraw",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "wei": wei_amount,
            "nonce": nonce_value,
        }
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            STAKING_SIGN_TYPES,
            "HyperliquidTransaction:CWithdraw",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def token_delegate(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        validator: str,
        is_undelegate: bool,
        wei_amount: int,
        nonce_value: int,
        nonce: int | None = None,
    ) -> dict:
        """Делегирование или отзыв делегирования нативного токена валидатору.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#delegate-or-undelegate-stake-from-validator
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "tokenDelegate",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "validator": validator,
            "isUndelegate": is_undelegate,
            "wei": wei_amount,
            "nonce": nonce_value,
        }
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            TOKEN_DELEGATE_TYPES,
            "HyperliquidTransaction:TokenDelegate",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def vault_transfer(
        self,
        vault_address: str,
        is_deposit: bool,
        usd: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        signing_vault_address: str | None = None,
    ) -> dict:
        """Перевод средств в или из хранилища.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#deposit-or-withdraw-from-a-vault
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "vaultTransfer",
            "vaultAddress": vault_address,
            "isDeposit": is_deposit,
            "usd": usd,
        }

        effective_vault = signing_vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def approve_agent(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        agent_address: str,
        nonce_value: int,
        agent_name: str | None = None,
        nonce: int | None = None,
    ) -> dict:
        """Одобрение API-кошелька.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#approve-an-api-wallet
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action: dict[str, Any] = {
            "type": "approveAgent",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "agentAddress": agent_address,
            "nonce": nonce_value,
        }
        if agent_name is not None:
            action["agentName"] = agent_name
        else:
            action["agentName"] = ""
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            APPROVE_AGENT_SIGN_TYPES,
            "HyperliquidTransaction:ApproveAgent",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def approve_builder_fee(
        self,
        hyperliquid_chain: Literal["Mainnet", "Testnet"],
        signature_chain_id: str,
        max_fee_rate: str,
        builder_address: str,
        nonce_value: int,
        nonce: int | None = None,
    ) -> dict:
        """Одобрение максимальной комиссии билдера.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#approve-a-builder-fee
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "approveBuilderFee",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "maxFeeRate": max_fee_rate,
            "builder": builder_address,
            "nonce": nonce_value,
        }
        action_nonce = nonce if nonce is not None else nonce_value
        is_mainnet = hyperliquid_chain == "Mainnet"
        signature = _sign_user_signed_action(
            self._wallet,
            action,
            APPROVE_BUILDER_FEE_SIGN_TYPES,
            "HyperliquidTransaction:ApproveBuilderFee",
            is_mainnet,
        )

        payload = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }

        return await self._post_request("/exchange", data=payload)

    async def place_twap_order(
        self,
        asset: int,
        is_buy: bool,
        size: str | float,
        reduce_only: bool,
        minutes: int,
        randomize: bool,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Создание TWAP-ордера.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#place-a-twap-order
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "twapOrder",
            "twap": {
                "a": asset,
                "b": is_buy,
                "s": str(size),
                "r": reduce_only,
                "m": minutes,
                "t": randomize,
            },
        }

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def cancel_twap_order(
        self,
        asset: int,
        twap_id: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Отмена TWAP-ордера.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-a-twap-order
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {
            "type": "twapCancel",
            "a": asset,
            "t": twap_id,
        }

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def reserve_request_weight(
        self,
        weight: int,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Резервирование дополнительного лимита действий.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#reserve-additional-actions
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {"type": "reserveRequestWeight", "weight": weight}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)

    async def invalidate_pending_nonce(
        self,
        nonce: int | None = None,
        expires_after: int | None = None,
        vault_address: str | None = None,
    ) -> dict:
        """Инвалидация ожидающего nonce без выполнения действия.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#invalidate-pending-nonce-noop
        """
        if self._wallet is None:
            raise NotAuthorized("Private key is required for private endpoints.")

        action = {"type": "noop"}

        effective_vault = vault_address or self._vault_address
        action_nonce = nonce if nonce is not None else int(time.time() * 1000)
        signature = _sign_l1_action(
            self._wallet,
            action,
            effective_vault,
            action_nonce,
            expires_after,
        )

        payload: dict[str, Any] = {
            "action": action,
            "nonce": action_nonce,
            "signature": signature,
        }
        if effective_vault is not None:
            payload["vaultAddress"] = effective_vault
        if expires_after is not None:
            payload["expiresAfter"] = expires_after

        return await self._post_request("/exchange", data=payload)
