from typing import Optional
import hmac
import hashlib
import os
import base64

import time

API_KEY: str = os.getenv("BITGET_API_KEY")  # type: ignore
API_SECRET: str = os.getenv("BITGET_API_SECRET")  # type: ignore
API_PASSPHRASE: str = os.getenv("BITGET_PASSPHRASE")  # type: ignore


def _ts_ms() -> str:
    return str(int(time.time() * 1000))


def _sign(
    timestamp: str, method: str, request_path: str, query: Optional[str], body: Optional[str]
) -> str:
    """
    ACCESS-SIGN = Base64(HMAC_SHA256(secret, prehash))
    prehash = timestamp + method.upper() + request_path + (?' + query if query else "") + (body or "")
    """
    method = method.upper()
    query_part = f"?{query}" if query else ""
    body_part = body or ""
    prehash = f"({timestamp}{method}{request_path}{query_part}{body_part}"
    digest = hmac.new(API_SECRET.encode("utf-8"), prehash.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def headers(
    method: str, request_path: str, query: Optional[str], body: Optional[str]
) -> dict[str, str]:
    ts = _ts_ms()
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": ts,
        "ACCESS-SIGN": _sign(ts, method, request_path, query, body),
        "Content-Type": "application/json",
        # "locale": "en-US", # по желанию
    }
