"""Модуль, который предоставляет дополнительные функции, которые нужны для внутренного использования в библиотеке."""

__all__ = [
    "dict_to_query_string",
    "generate_hmac_sha256_signature",
    "sort_params_by_alphabetical_order",
    "filter_params",
]

import base64
import hashlib
import hmac
import json
from typing import Literal
from urllib.parse import urlencode


def filter_params(params: dict) -> dict:
    """Фильтрует параметры запроса, удаляя None-значения.

    Параметры:
        params (`dict`): Словарь параметров запроса.

    Возвращает:
        `dict`: Отфильтрованный словарь параметров запроса.
    """
    return {k: v for k, v in params.items() if v is not None}


def sort_params_by_alphabetical_order(params: dict) -> dict:
    """Сортирует параметры запроса по алфавиту.

    Параметры:
        params (`dict`): Словарь параметров запроса.

    Возвращает:
        `dict`: Отсортированный словарь параметров запроса.
    """
    return dict(sorted(params.items()))


def dict_to_query_string(params: dict) -> str:
    """Преобразует словарь параметров в query string для URL.

    - Списки и словари автоматически сериализуются в JSON.
    - Используется стандартная urlencode кодировка.

    Параметры:
        params (`dict`): Словарь параметров запроса.

    Возвращает:
        `str`: Строка параметров, готовая для использования в URL.
    """
    processed = {
        k: json.dumps(v, separators=(",", ":")) if isinstance(v, list | dict) else v
        for k, v in params.items()
    }
    return urlencode(processed, doseq=True)


def generate_hmac_sha256_signature(
    secret_key: str,
    payload: str,
    encoding: Literal["hex", "base64"] = "hex",
) -> str:
    """Генерирует HMAC-SHA256 подпись.

    encoding:
        - "hex" → шестнадцатеричная строка
        - "base64" → base64-строка
    """
    digest = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    if encoding == "hex":
        return digest.hex()
    elif encoding == "base64":
        return base64.b64encode(digest).decode()
    else:
        raise ValueError("encoding must be 'hex' or 'base64'")
