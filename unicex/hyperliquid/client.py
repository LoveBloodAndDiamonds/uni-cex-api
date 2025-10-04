__all__ = ["Client"]

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


def l1_payload(phantom_agent: dict[str, Any]) -> dict[str, Any]:
    """Формирует EIP-712 payload для подписи "агента".

    Простыми словами:
    Это упаковка данных в формат, который кошелёк сможет подписать.
    В Ethereum есть стандарт EIP-712 — "structured data signing".
    Он позволяет подписывать не просто строку, а структуру (объект),
    чтобы потом её можно было проверить.

    Пример:
        >>> phantom = {"source": "a", "connectionId": b"1234...."}
        >>> l1_payload(phantom)
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


def address_to_bytes(address: str) -> bytes:
    r"""Переводит Ethereum-адрес в байты.

    Простыми словами:
    Берём строку вида "0xABC123..." и превращаем её в бинарные данные.
    Это нужно, потому что внутри подписи адрес должен храниться как массив байтов.

    Пример:
        >>> address_to_bytes("0x0000000000000000000000000000000000000001")
        b'\\x00...\\x01'

    Параметры:
        address (str): строковый Ethereum-адрес, с "0x" или без.

    Возвращает:
        bytes: бинарное представление адреса.
    """
    return bytes.fromhex(address[2:] if address.startswith("0x") else address)


def construct_phantom_agent(hash: bytes, is_mainnet: bool) -> dict[str, Any]:
    r"""Собирает объект "phantom_agent".

    Простыми словами:
    Это кусочек данных, который будет подписываться.
    В нём указывается:
    - источник ("a" если это mainnet, "b" если не mainnet)
    - connectionId — хэш действий.

    Пример:
        >>> construct_phantom_agent(b"\\x01" * 32, True)
        {"source": "a", "connectionId": b"\\x01"*32}

    Параметры:
        hash (bytes): хэш действия (32 байта).
        is_mainnet (bool): True если сеть основная, False если тестовая.

    Возвращает:
        dict: объект phantom_agent.
    """
    return {"source": "a" if is_mainnet else "b", "connectionId": hash}


def action_hash(
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
        >>> action_hash(action, None, 42, None)
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
        data += address_to_bytes(vault_address)
    if expires_after is not None:
        data += b"\x00"
        data += expires_after.to_bytes(8, "big")
    return keccak(data)


def sign_inner(wallet: LocalAccount, data: dict[str, Any]) -> dict[str, Any]:
    """Подписывает данные EIP-712 через кошелёк.

    Простыми словами:
    Берём структуру (payload), кодируем её в формат EIP-712
    и просим кошелёк подписать.
    Возвращаем r, s, v — стандартные параметры Ethereum-подписи.

    Пример:
        >>> sign_inner(wallet, {...})
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


def sign_l1_action(
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
        >>> sign_l1_action(wallet, {"type": "order"}, None, 1, None, True)
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
    hash = action_hash(action, active_pool, nonce, expires_after)
    phantom_agent = construct_phantom_agent(hash, is_mainnet)
    data = l1_payload(phantom_agent)
    return sign_inner(wallet, data)


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

    async def metadata(self, dex: str | None = None) -> dict:
        """Получение метаинформации о бирже.

        https://docs.chainstack.com/reference/hyperliquid-info-meta
        """
        payload = {
            "type": "meta",
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def spot_metadata(self) -> dict:
        """Получение спотовой метаинформации о бирже.

        https://docs.chainstack.com/reference/hyperliquid-info-spotmeta
        """
        payload = {"type": "spotMeta"}

        return await self._post_request("/info", data=payload)

    async def clearinghouse_state(self, user: str, dex: str | None = None) -> dict:
        """Получение сводки по фьючерсному аккаунту пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-clearinghousestate
        """
        payload = {
            "type": "clearinghouseState",
            "user": user,
            "dex": dex,
        }

        return await self._post_request("/info", data=payload)

    async def spot_clearinghouse_state(self, user: str) -> dict:
        """Получение информации о балансе спотового аккаунта пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-spotclearinghousestate
        """
        payload = {
            "type": "spotClearinghouseState",
            "user": user,
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

    async def active_asset_data(self, user: str, coin: str) -> dict:
        """Получение сведений об активном фьючерсном активе пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-activeassetdata
        """
        payload = {
            "type": "activeAssetData",
            "user": user,
            "coin": coin,
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

    async def spot_deploy_state(self, user: str) -> dict:
        """Получение состояния системы деплоя спотовых токенов.

        https://docs.chainstack.com/reference/hyperliquid-info-spotdeploystate
        """
        payload = {
            "type": "spotDeployState",
            "user": user,
        }

        return await self._post_request("/info", data=payload)

    async def perp_deploy_auction_status(self) -> dict:
        """Получение статуса аукционов деплоя перпетуалов.

        https://docs.chainstack.com/reference/hyperliquid-info-perpdeployauctionstatus
        """
        payload = {"type": "perpDeployAuctionStatus"}

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

    async def perp_dexs(self) -> list[dict | None]:
        """Получение списка доступных перпетуальных DEX.

        https://docs.chainstack.com/reference/hyperliquid-info-perpdexs
        """
        payload = {"type": "perpDexs"}

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

    async def perps_at_open_interest_cap(self) -> list[str]:
        """Получение списка перпетуалов на предельном открытом интересе.

        https://docs.chainstack.com/reference/hyperliquid-info-perps-at-open-interest-cap
        """
        payload = {"type": "perpsAtOpenInterestCap"}

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

    async def user_fills(self, user: str, aggregate_by_time: bool | None = None) -> list[dict]:
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
        self, users: list[str], dex: str | None = None
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
        interval: Literal[
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ],
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

    async def meta_and_asset_contexts(self) -> list[Any]:
        """Получение метаданных и рыночных метрик по перпетуалам.

        https://docs.chainstack.com/reference/hyperliquid-info-meta-and-asset-ctxs
        """
        payload = {"type": "metaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def user_funding(
        self, user: str, start_time: int, end_time: int | None = None
    ) -> list[Any]:
        """Получение истории фандинга пользователя.

        https://docs.chainstack.com/reference/hyperliquid-info-user-funding
        """
        payload = {
            "type": "userFunding",
            "user": user,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def funding_history(
        self, coin: str, start_time: int, end_time: int | None = None
    ) -> list[dict]:
        """Получение истории ставок фандинга по активу.

        https://docs.chainstack.com/reference/hyperliquid-info-funding-history
        """
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._post_request("/info", data=payload)

    async def predicted_fundings(self) -> list[Any]:
        """Получение прогнозных ставок фандинга по всем перпетуалам.

        https://docs.chainstack.com/reference/hyperliquid-info-predicted-fundings
        """
        payload = {"type": "predictedFundings"}

        return await self._post_request("/info", data=payload)

    async def spot_meta_and_asset_contexts(self) -> list[Any]:
        """Получение метаданных и метрик для спотовых активов.

        https://docs.chainstack.com/reference/hyperliquid-info-spot-meta-and-asset-ctxs
        """
        payload = {"type": "spotMetaAndAssetCtxs"}

        return await self._post_request("/info", data=payload)

    async def gossip_root_ips(self) -> list[str]:
        """Получение списка узлов для P2P-госсипа.

        https://docs.chainstack.com/reference/hyperliquid-info-gossip-root-ips
        """
        payload = {"type": "gossipRootIps"}

        return await self._post_request("/info", data=payload)

    async def token_details(self, token_id: str) -> dict:
        """Получение подробной информации о токене.

        https://docs.chainstack.com/reference/hyperliquid-info-token-details
        """
        payload = {
            "type": "tokenDetails",
            "tokenId": token_id,
        }

        return await self._post_request("/info", data=payload)

    async def place_order(self, *args, **kwargs) -> dict:
        """Выставление ордера на бирже. Обертка над методом `batch_place_orders`.

        https://docs.chainstack.com/reference/hyperliquid-exchange-place-order
        """
        order = {}
        await self.batch_place_orders([order])

    async def batch_place_orders(self, orders: list[dict], builder: str | None = None) -> dict:
        """Выставление пакета ордеров на бирже.

        https://docs.chainstack.com/reference/hyperliquid-exchange-place-order
        """
        if not self._wallet:
            raise NotAuthorized("Private key required to private request")

        order_action = {
            "type": "order",
            "orders": orders,
            "grouping": "na",
        }
        if builder:
            order_action["builder"] = builder

        # return await self._post_request("/exchange", data=data)
