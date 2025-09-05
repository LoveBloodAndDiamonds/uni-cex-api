import hashlib
import hmac
import os
import time
import requests
import orjson
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


class SyncClient:
    API_URL = "https://api.bybit.com/"
    API_VERSION = "v5"

    REQUEST_TIMEOUT: float = 5

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        receive_window: int = 5000,
    ):
        self.API_KEY = api_key
        self.API_SECRET: RSAPrivateKey | str
        self.API_SECRET = api_secret
        self.receive_window = receive_window
        self.timestamp_offset = 0
        self.base = self.API_URL
        self.base_url = os.path.join(self.base, self.API_VERSION, "")
        self.session = requests.Session()

    def _get_headers(self, timestamp_milli: int, signed=False) -> dict[str, str]:
        headers = {
            "X-BAPI-TIMESTAMP": str(timestamp_milli),
            "X-BAPI-RECV-WINDOW": str(self.receive_window),
        }
        if signed:
            headers["X-BAPI-API-KEY"] = self.API_KEY
        return headers

    def _create_api_uri(self, path: str) -> str:
        return os.path.join(self.base, self.API_VERSION, path)

    def _generate_signature(
        self, method: str, url: str, params: dict, body: str, timestamp_milli: int
    ) -> str:
        if method.upper() == "GET":
            prepared_str = (
                str(timestamp_milli)
                + self.API_KEY
                + str(self.receive_window)
                + (url.split("?")[1] if "?" in url else "")
            )
        else:
            prepared_str = str(timestamp_milli) + self.API_KEY + str(self.receive_window) + body
        prepared_bytes = prepared_str.encode("utf-8")
        return hmac.new(self.API_SECRET.encode("utf-8"), prepared_bytes, hashlib.sha256).hexdigest()

    def _request(self, method: str, path: str, signed: bool = False, **kwargs):
        timestamp = int(time.time() * 1000 + self.timestamp_offset)
        url = self._create_api_uri(path)

        headers = self._get_headers(timestamp, signed)
        data = None
        params = None
        if method.lower() == "get":
            params = kwargs
        else:
            data = orjson.dumps(kwargs).decode("utf-8")

        if signed:
            signature = self._generate_signature(method, url, params or {}, data or "", timestamp)
            headers["X-BAPI-SIGN"] = signature
            headers["X-BAPI-SIGN-TYPE"] = "2"

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=self.REQUEST_TIMEOUT,
        )
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response):
        if not response.ok:
            raise ConnectionError(f"{response=}, {response.status_code=}, {response.text=}")
        try:
            return orjson.loads(response.text)
        except ValueError:
            raise ValueError(f"Invalid Response: {response.text}")

    # --- удобные шорткаты ---
    def get(self, path: str, signed: bool = False, **kwargs):
        return self._request("GET", path, signed, **kwargs)

    def post(self, path: str, signed: bool = False, **kwargs):
        return self._request("POST", path, signed, **kwargs)

    def put(self, path: str, signed: bool = False, **kwargs):
        return self._request("PUT", path, signed, **kwargs)

    def delete(self, path: str, signed: bool = False, **kwargs):
        return self._request("DELETE", path, signed, **kwargs)
