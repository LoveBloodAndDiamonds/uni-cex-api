import base64
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto
import requests
from abc import ABC, abstractmethod


class ExchangeName(Enum):
    BINANCE = auto()
    OKX = auto()
    BITGET = auto()
    KUCOIN = auto()
    MEXC = auto()
    GATEIO = auto()
    BYBIT = auto()
    KRAKEN = auto()
    BTSE = auto()
    BITRUE = auto()


@dataclass
class ExchangeConfig:
    api_key: str
    api_secret: str
    base_url: Optional[str] = None
    api_passphrase: Optional[str] = None


class Exchange(ABC):
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self.base_url = config.base_url or self.get_default_base_url()

    @abstractmethod
    def get_default_base_url(self) -> str:
        pass

    @abstractmethod
    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        pass

    def send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> str:
        url = self.base_url + endpoint
        params, headers = self._prepare_request(method, endpoint, params, signed)

        response = requests.request(method, url, headers=headers, params=params)
        return response.text


class Binance(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.binance.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        if signed:
            timestamp = int(time.time() * 1000)
            if params is None:
                params = {}
            params["timestamp"] = timestamp
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            signature = hmac.new(
                self.config.api_secret.encode(), query_string.encode(), hashlib.sha256
            ).hexdigest()
            params["signature"] = signature
        headers = {
            "X-MBX-APIKEY": self.config.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return params, headers


class OKX(Exchange):
    def get_default_base_url(self) -> str:
        return "https://www.okx.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        timestamp = (
            datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        )
        headers = {
            "OK-ACCESS-KEY": self.config.api_key,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.config.api_passphrase,
            "Content-Type": "application/json",
        }

        if signed:
            if method == "GET":
                params_str = ""
                if params:
                    sorted_params = sorted(params.items())
                    params_str = "?" + urlencode(sorted_params)
                prehash = timestamp + method + endpoint + params_str
            else:
                prehash = timestamp + method + endpoint + (json.dumps(params) if params else "")

            signature = base64.b64encode(
                hmac.new(self.config.api_secret.encode(), prehash.encode(), hashlib.sha256).digest()
            ).decode()
            headers["OK-ACCESS-SIGN"] = signature

        return params, headers


class Bitget(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.bitget.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        timestamp = str(int(time.time_ns() / 1000000))
        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.config.api_key,
            "ACCESS-TIMESTAMP": timestamp,
        }

        if signed:
            if params is None:
                params = {}
            prehash = timestamp + method.upper() + endpoint + (json.dumps(params) if params else "")
            signature = hmac.new(
                bytes(self.config.api_secret, encoding="utf8"),
                bytes(prehash, encoding="utf-8"),
                digestmod="sha256",
            ).digest()
            signature = base64.b64encode(signature).decode()
            headers.update(
                {
                    "ACCESS-SIGN": signature,
                    "ACCESS-PASSPHRASE": self.config.api_passphrase,
                }
            )

        return params, headers


class Kucoin(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.kucoin.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        timestamp = str(int(time.time() * 1000))
        if signed:
            if params is None:
                params = {}
            str_to_sign = (
                timestamp + method.upper() + endpoint + (json.dumps(params) if params else "")
            )
            signature = base64.b64encode(
                hmac.new(
                    self.config.api_secret.encode(), str_to_sign.encode(), hashlib.sha256
                ).digest()
            ).decode()
        else:
            signature = ""
        headers = {
            "KC-API-KEY": self.config.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": self.config.api_passphrase,
            "Content-Type": "application/json",
        }
        return params, headers


class MEXC(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.mexc.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        headers = {"X-MEXC-APIKEY": self.config.api_key, "Content-Type": "application/json"}

        if signed:
            timestamp = str(int(time.time() * 1000))
            if params is None:
                params = {}
            params["timestamp"] = timestamp

            if method == "GET":
                query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            else:
                query_string = json.dumps(params)

            signature = hmac.new(
                self.config.api_secret.encode(), query_string.encode(), hashlib.sha256
            ).hexdigest()
            params["signature"] = signature

        return params, headers


class GateIO(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.gateio.ws"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        timestamp = str(int(time.time()))
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "KEY": self.config.api_key,
            "Timestamp": timestamp,
        }
        if signed:
            if params is None:
                params = {}
            payload_string = json.dumps(params) if method != "GET" else ""
            query_string = (
                "&".join([f"{k}={v}" for k, v in params.items()]) if method == "GET" else ""
            )
            m = hashlib.sha512()
            m.update(payload_string.encode("utf-8"))
            hashed_payload = m.hexdigest()
            signature_string = (
                f"{method}\n{endpoint}\n{query_string}\n{hashed_payload}\n{timestamp}"
            )
            signature = hmac.new(
                self.config.api_secret.encode("utf-8"),
                signature_string.encode("utf-8"),
                hashlib.sha512,
            ).hexdigest()
            headers.update({"SIGN": signature})
        return params, headers


class Bybit(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.bybit.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": self.config.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
        }
        if signed:
            if params is None:
                params = {}
            query_string = "&".join([f"{k}={v}" for k, v in params.items()]) if params else ""
            if method == "GET":
                signature_payload = f"{timestamp}{self.config.api_key}{recv_window}{query_string}"
            else:
                body_string = json.dumps(params)
                signature_payload = f"{timestamp}{self.config.api_key}{recv_window}{body_string}"
            signature = hmac.new(
                self.config.api_secret.encode("utf-8"),
                signature_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers["X-BAPI-SIGN"] = signature

        return params, headers


class Kraken(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.kraken.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Key": self.config.api_key,
            "API-Sign": "",
        }
        if signed:
            if params is None:
                params = {}
            if "nonce" not in params:
                params["nonce"] = str(int(time.time() * 1000))
            postdata = urlencode(params)
            message = (
                endpoint.encode() + hashlib.sha256((params["nonce"] + postdata).encode()).digest()
            )
            signature = hmac.new(
                base64.b64decode(self.config.api_secret), message, hashlib.sha512
            ).digest()
            headers["API-Sign"] = base64.b64encode(signature).decode()
        return params, headers


class BTSE(Exchange):
    def get_default_base_url(self) -> str:
        return "https://api.btse.com/spot"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        headers = {"Content-Type": "application/json"}

        if signed:
            request_nonce = str(int(time.time() * 1000))
            body_str = ""
            if method == "POST" and params:
                body_str = json.dumps(
                    params, separators=(",", ":"), sort_keys=True, ensure_ascii=False
                )

            concatenated_str = endpoint + request_nonce + body_str
            signature = hmac.new(
                self.config.api_secret.encode("utf-8"),
                concatenated_str.encode("utf-8"),
                hashlib.sha384,
            ).hexdigest()

            headers.update(
                {
                    "request-api": self.config.api_key,
                    "request-nonce": request_nonce,
                    "request-sign": signature,
                }
            )

        return params, headers


class Bitrue(Exchange):
    def get_default_base_url(self) -> str:
        return "https://www.bitrue.com"

    def _prepare_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]], signed: bool
    ) -> tuple:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",  # Changed to x-www-form-urlencoded
            "X-MBX-APIKEY": self.config.api_key,
        }

        if signed:
            if params is None:
                params = {}
            params["recvWindow"] = 5000
            params["timestamp"] = str(int(time.time() * 1000))

            signature = self._generate_signature(params)
            params["signature"] = signature

        return params, headers

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        signature = hmac.new(
            self.config.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature


class ExchangeFactory:
    @staticmethod
    def create_exchange(exchange_name: ExchangeName, config: ExchangeConfig) -> Exchange:
        exchanges = {
            ExchangeName.BINANCE: Binance,
            ExchangeName.OKX: OKX,
            ExchangeName.BITGET: Bitget,
            ExchangeName.KUCOIN: Kucoin,
            ExchangeName.MEXC: MEXC,
            ExchangeName.GATEIO: GateIO,
            ExchangeName.BYBIT: Bybit,
            ExchangeName.KRAKEN: Kraken,
            ExchangeName.BTSE: BTSE,
            ExchangeName.BITRUE: Bitrue,
        }
        if exchange_name in exchanges:
            return exchanges[exchange_name](config)
        else:
            raise ValueError(f"Exchange {exchange_name} is not supported.")
