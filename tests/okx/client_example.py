import base64
import datetime
import hashlib
import hmac
import json
from typing import Literal

import aiohttp


class OkxClient:
    BASE_URL = "https://www.okx.com"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_passphrase: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.api_passphrase = api_passphrase
        self.session = session or aiohttp.ClientSession()

    def _get_timestamp(self) -> str:
        now = datetime.datetime.now(tz=datetime.UTC).replace(tzinfo=None)
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def _get_signature(self, timestamp: str, method: str, path: str, body: str) -> str:
        message = f"{timestamp}{method}{path}{body}"
        h = hmac.new(self.api_secret, message.encode(), hashlib.sha256)
        return base64.b64encode(h.digest()).decode()

    def _prepare_headers(self, method: str, path: str, body: str) -> dict:
        timestamp = self._get_timestamp()
        signature = self._get_signature(timestamp, method, path, body)
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.api_passphrase,
            "Content-Type": "application/json",
            "x-simulated-trading": "0",
        }

    async def create_order(
        self,
        inst_id: str,
        side: Literal["buy", "sell"],
        ord_type: Literal["market", "limit"],
        sz: str,
        px: str | None = None,
        cl_ord_id: str | None = None,
    ) -> dict:
        path = "/api/v5/trade/order"
        url = self.BASE_URL + path
        body = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": side,
            "ordType": ord_type,
            "sz": sz,
        }

        if px is not None:
            body["px"] = px
        if cl_ord_id:
            body["clOrdId"] = cl_ord_id

        json_body = json.dumps(body)
        headers = self._prepare_headers("POST", path, json_body)

        async with self.session.post(url, headers=headers, json=body) as resp:
            return await resp.json()

    async def cancel_order(
        self, inst_id: str, ord_id: str | None = None, cl_ord_id: str | None = None
    ) -> dict:
        path = "/api/v5/trade/cancel-order"
        url = self.BASE_URL + path
        body = {"instId": inst_id}
        if ord_id:
            body["ordId"] = ord_id
        elif cl_ord_id:
            body["clOrdId"] = cl_ord_id
        else:
            raise ValueError("Нужно указать ord_id или cl_ord_id")

        json_body = json.dumps(body)
        headers = self._prepare_headers("POST", path, json_body)

        async with self.session.post(url, headers=headers, json=body) as resp:
            return await resp.json()

    async def get_order_status(
        self, inst_id: str, ord_id: str | None = None, cl_ord_id: str | None = None
    ) -> dict:
        path = "/api/v5/trade/order"
        url = self.BASE_URL + path

        params = {"instId": inst_id}
        if ord_id:
            params["ordId"] = ord_id
        elif cl_ord_id:
            params["clOrdId"] = cl_ord_id
        else:
            raise ValueError("Нужно указать ord_id или cl_ord_id")

        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        headers = self._prepare_headers("GET", path + query, "")

        async with self.session.get(url, headers=headers, params=params) as resp:
            return await resp.json()

    async def get_positions(self, inst_id: str) -> dict:
        """https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions"""
        path = "/api/v5/account/positions"
        url = self.BASE_URL + path
        params = {"instId": inst_id}
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        headers = self._prepare_headers("GET", path + query, "")

        async with self.session.get(url, headers=headers, params=params) as resp:
            return await resp.json()

    async def get_balances(self, ccy: str | None = None) -> dict:
        """https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance"""
        path = "/api/v5/account/balance"
        url = self.BASE_URL + path
        params = {}
        if ccy:
            params["ccy"] = ccy
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        headers = self._prepare_headers("GET", path + query, "")

        async with self.session.get(url, headers=headers, params=params) as resp:
            return await resp.json()

    async def close(self):
        await self.session.close()
